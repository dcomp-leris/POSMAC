"""
Created on Sun Apr 28 22:16:09 2024
@author: alireza
Ver: 2.00 
Developed in Leris Lab
Presented in IEEE NFV-SDN 2024 Conference
"""

# import required packages
import logging, time, hashlib, socket, yaml, re, os
from scapy.all import sniff, sendp, UDP, Ether, IP
from queue import Queue, Empty
from packet_classifier import PacketClassifier
import mytimelog as mydb


''' General Variables '''
#config_file = '/home/cls/config.yaml'
config_file = 'config.yaml'
# Model path configuration  dt_model.joblib
# model_path = '/home/cls/dt_model.joblib'
#model_path = '/home/cls/mymodel/dt.joblib' # default
#model_path = '/home/cls/rf_model.joblib'

# Network configuration
# Interface listen to TG (eth4) (IP = 10.10.10.3) (MAC = 00:00:00:00:ac:01) 
SRC_INTERFACE = 'eth4'  
# Container Table [Assign the Physical interface to specific APPs]
# eth1==> ar (IP = 192.168.10:2) dst_IP = 120.120.120.1
# eth2==> cg (IP = 192.168.20.2) dst_IP = 130.130.130.1
# eth3==> other (IP = 192.168.30.2) dst_IP = 140.140.140.1
container_table = {
    'AR': ['eth1', '00:00:00:00:ac:02', '00:00:00:00:0a:01'],
    'CG': ['eth2', '00:00:00:00:ac:03', '00:00:00:00:0b:01'], 
    'Other': ['eth3', '00:00:00:00:ac:04', '00:00:00:00:0c:01']
}

# AR/CG/Other Server IP 
ar = '120.120.120.1' #container_table['AR'][3] #'120.120.120.1'
cg = '130.130.130.1'                # container_table['CG'][3]  #'130.130.130.1'
other = '140.140.140.1' # container_table['Other'][3] #'140.140.140.1'

# Store the flows to avoid sending of the consecutive packets of the flows
lookup_table = {} # lookup table to cache the  packets of the flow

# logging and counting the packets
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') # added to track the packets

# Initialize counters
packets_received = 0
packets_forwarded = 0


# Packet and time counter
cached_pkt_start = 0
cached_pkt_end = 0

cached_time_start =0
cached_time_end =0


cached_pkts = 0
cached_time = 0

# load the Classifier
#classifier = PacketClassifier(model_path)

# Global variables for monitoring
#packets_forwarded = 0
bytes_forwarded = 0
start_time = time.time()
q_cache = Queue()


# Assuming classifier and container_table are defined elsewhere
global last_reset_time 
last_reset_time = time.time()
lookup_table = {}



''' Functions Definition '''
# load configuration Yaml files
def load_config(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Find last Trained joblib file (Ordering in Transfer Learning)
def find_latest_file_by_modification(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith("ml") and f.endswith(".joblib")]
    latest_file = max(files, key=os.path.getmtime, default=None)
    return latest_file


# Set the reset time for lookup table
reset_time  = 8000  	# it is set with config file to reset the lookuptable for forwarding 
entry_num = 0		# it is set with config file


# reset lookup table for tune number of classification operation
def reset_lookup_table_if_needed():
    global lookup_table, last_reset_time 
    current_time = time.time()
    if (current_time - last_reset_time) * 1000 >= reset_time or len(lookup_table) >= entry_num:  # Check if 100ms have passed
        lookup_table = {}  # Reset the table
        last_reset_time = current_time
        #classifier = PacketClassifier(model_path) # model_path
    # elif (current_time - last_reset_time) * 1000 <= (reset_time): 
        mylast_ml_model = find_latest_file_by_modification(model_path_folder)     # '/home/cls/mymlcache')
        #print("***************************************",mylast_ml_model,"************************************")
        classifier = PacketClassifier(mylast_ml_model) # model_path)

pkt_counter_ar = 0; pkt_counter_cg = 0; pkt_counter_other = 0
egress_counter_ar = 0; egress_counter_cg = 0; egress_counter_other = 0

# Receive & Forward Packets
def forward_packet(packet):
    
    global packets_forwarded, bytes_forwarded, lookup_table, q_cache, i , packets_received, classifier, pkt_counter_ar, pkt_counter_cg, pkt_counter_other, egress_counter_ar, egress_counter_cg, egress_counter_other
    #received_time = time.time()
    #hasher.digest()
    reset_lookup_table_if_needed()  # Check if it's time to reset the lookup_table

    if IP in packet and UDP in packet:       # Check the protocol for preventing error rising
        received_time = time.time() # UDP packet timestamp
        bytes_forwarded += len(packet)
        flowkey_local = hashlib.sha256(str((packet[IP].src, packet[IP].dst, packet[UDP].dport)).encode().hex().encode()).hexdigest()  
        flowkey_reverse =  hashlib.sha256(str((packet[IP].dst, packet[IP].src, packet[UDP].dport)).encode().hex().encode()).hexdigest() 
        
        # logging
        packets_received += 1
        print(f'pkt_type:receiving,pkt_no:{packets_received},from:{packet[IP].src},to: {packet[IP].dst},iface:{SRC_INTERFACE},',"Time:", received_time) #time.time())
        #logging.debug(f"Received packet from {packet[IP].src} to {packet[IP].dst}")
        #if packet[IP].dst == ar: 
            #pkt_counter_ar = pkt_counter_ar + 1
            #print('AR pkt num: ',pkt_counter_ar) 

        if packet[IP].dst == ar: 
            pkt_counter_ar = pkt_counter_ar + 1
            print('AR pkt num: ',pkt_counter_ar)
        elif packet[IP].dst == cg:
            pkt_counter_cg = pkt_counter_cg + 1
            print('CG pkt num: ',pkt_counter_cg)
        elif packet[IP].dst == other:
            pkt_counter_other = pkt_counter_other + 1
            print('Other pkt num: ',pkt_counter_other)




        if flowkey_local in lookup_table.keys():
            iface, src_mac, dst_mac = container_table[lookup_table[flowkey_local]]
            forwarded_packet = Ether(src=src_mac, dst=dst_mac) / packet[IP]
            sendp(forwarded_packet, iface=iface, verbose=False)
            packets_forwarded += 1
            print('************************************************')
            print(f'pkt_type:forwarding[lookup],pkt_no:{packets_forwarded},from:{forwarded_packet[IP].src},to: {forwarded_packet[IP].dst},iface:{iface},',"Forwarding Delay Time:", time.time()-received_time)
            mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'forwarding'},{'delay': (time.time()-received_time)*1000}) ## log classification delay
            if forwarded_packet[IP].dst == ar and iface != container_table['AR'][0]: 
                egress_counter_ar = egress_counter_ar + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_ar - egress_counter_ar)/pkt_counter_ar)})
                print('AR pkt percentage: ',((pkt_counter_ar - egress_counter_ar)/pkt_counter_ar))
            elif forwarded_packet[IP].dst == cg and iface != container_table['CG'][0]:
                pkt_counter_cg = pkt_counter_cg + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg)})
                print('CG pkt percentage: ',((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg))
            elif forwarded_packet[IP].dst == other and iface != container_table['Other'][0]:
                pkt_counter_other = pkt_counter_other + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_other - egress_counter_other)/pkt_counter_other)})
                print('Other pkt percentage: ',((pkt_counter_other - egress_counter_other)/pkt_counter_other))
 

            print('************************************************')
        
        else:
            # Classification the packet
            result = classifier.classify_packet(packet)
            if not result or len(result)==2 or len(result)==1 or result[1] is None or len(result)<3: 
                q_cache.put([flowkey_local,packet])
                return
            flow_class = "AR" if result[1] in ('AR_UL', 'AR_DL' ,'AR') else "CG" if result[1] in ('CG_UL', 'CG_DL','CG') else "Other"
            lookup_table[flowkey_local] = flow_class # result[0]] = flow_class
            print(f"====================")    # Received pkts {packets_received}")
            print('Forwarding starts:',(packet[IP].src,packet[IP].dst,packet[UDP].dport),'==>',flow_class)
            print(f'Features [{result[2]}]', 'Classification Delay:', (time.time()-received_time))
            mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": packet[IP].dst, "type": 'classification'},{'delay': (time.time()-received_time)*1000}) ## log classification delay
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(str([(packet[IP].src,packet[IP].dst,packet[UDP].sport,packet[UDP].dport),result[2],result[1]]).encode(), ('192.168.140.3', 12348))
            print("====================")


            # Limit lookup_table to 10 entries
            '''if len(lookup_table) >= entry_num:
            # This is a simple way to remove an entry; you may want to refine this logic
                lookup_table.pop(next(iter(lookup_table)))  # Remove an arbitrary (the first) entry'''
            

            #if result[0] not in lookup_table:
                #lookup_table[result[0]] = flow_class

            iface, src_mac, dst_mac = container_table[flow_class] #lookup_table[result[0]]]
            forwarded_packet = Ether(src=src_mac, dst=dst_mac) / packet[IP]
            


            #cached_pkt_start = 0 
            #cached_pkt_end = 0
            #cached_time_start =0
            #cached_time_end =0
            cached_pkts = 0
            cached_time = 0

            cached_time_start = time.time()
            while not q_cache.empty():
                cache_packet = None 
                #cached_pkt_start = packets_forwarded # To calculate cached packets to classification
                cached_pkts+=1
                #cached_time_start = time.time()
                cache_packet= q_cache.get()
                #print('cache packet--?',cache_packet)
                #hasher.digest()
                #if result[0] not in lookup_table:
                #lookup_table[result[0]] = flow_class
                if  (flowkey_local in cache_packet[0]) or (flowkey_reverse in cache_packet[0]):
                    my_pkt = Ether(src=src_mac, dst=dst_mac) / cache_packet[1][IP]
                    sendp(my_pkt, iface=iface, verbose=False)
                    packets_forwarded += 1  
                    print(f'pkt_type:forwarding[cached],pkt_no:{packets_forwarded},from:{forwarded_packet[IP].src},to: {forwarded_packet[IP].dst},iface:{iface},',"Time:", time.time()-received_time)
                    mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'forwarding'},{'delay': (time.time()-received_time)*1000}) ## log classification delay
                    if forwarded_packet[IP].dst == ar and iface != container_table['AR'][0]: #'eth1': 
                        egress_counter_ar = egress_counter_ar + 1
                        mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_ar - egress_counter_ar)/pkt_counter_ar)})
                        print('AR pkt percentage: ',((pkt_counter_ar-egress_counter_ar)/pkt_counter_ar))
                    elif forwarded_packet[IP].dst == cg and iface != container_table['CG'][0]: #=='eth2':
                        egress_counter_cg = egress_counter_cg + 1
                        mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg)})
                        print('CG pkt percentage: ',((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg))
                    elif forwarded_packet[IP].dst == other and iface==container_table['Other'][0]: #'eth3':
                        egress_counter_other = egress_counter_other + 1
                        mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_other - egress_counter_other)/pkt_counter_other)})
                        print('Other pkt percentage: ',((pkt_counter_other - egress_counter_other)/pkt_counter_other))
 





                else:
                    continue
            cached_time = time.time() - cached_time_start
            mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'cache'},{'delay': (time.time()-received_time)*1000}) ## log classification delay
            print(f'caching time for classification is {cached_time}')
            sendp(forwarded_packet, iface=iface, verbose=False)

            if forwarded_packet[IP].dst == ar and iface != container_table['Other'][0]: #'eth1': 
                egress_counter_ar = egress_counter_ar + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_ar - egress_counter_ar)/pkt_counter_ar)})
                print('AR pkt percentage: ',((pkt_counter_ar -egress_counter_ar)/pkt_counter_ar))
            elif forwarded_packet[IP].dst == cg and iface != container_table['CG'][0]: #'eth2':
                egress_counter_cg = egress_counter_cg + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg)})
                print('CG pkt percentage: ',((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg))
            elif forwarded_packet[IP].dst == other and iface != container_table['Other'][0]:  #'eth3':
                egress_counter_other = egress_counter_other + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_other - egress_counter_other)/pkt_counter_other)})
                print('Other pkt percentage: ',((pkt_counter_other - egress_counter_other)/pkt_counter_other))
 

            # logging
            #print('Forwarded', time.time())
            packets_forwarded += 1
            #cached_pkt_end = packets_forwarded
            #cached_pkts = int(cached_pkt_end) - int(cached_pkt_start)
            #cached_time_end = time.time() 
            #cached_time = cached_time_end - cached_time_start
            #print(f'Forwarded packet {packets_forwarded}  from {forwarded_packet[IP].src} to {forwarded_packet[IP].dst} on iface {iface}', time.time())
            print(f'pkt_type:forwarding[classified],pkt_no:{packets_forwarded},from:{forwarded_packet[IP].src},to: {forwarded_packet[IP].dst},iface:{iface},',"Time:", time.time()-received_time)  
            mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'classification'},{'delay': (time.time()-received_time)*1000}) ## log classification delay
            #'c_time: ',cached_time, 'c_pkts: ', cached_pkts)

            if forwarded_packet[IP].dst == ar and iface != container_table['AR'][0]: #'eth1': 
                egress_counter_ar = egress_counter_ar + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_ar - egress_counter_ar)/pkt_counter_ar)})
                print('AR pkt percentage: ',((pkt_counter_ar - egress_counter_ar)/pkt_counter_ar))
            elif forwarded_packet[IP].dst == cg and iface !=container_table['CG'][0]:  #'eth2':
                egress_counter_cg = egress_counter_cg + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg)})
                print('CG pkt percentage: ',((pkt_counter_cg - egress_counter_cg)/pkt_counter_cg))
            elif forwarded_packet[IP].dst == other and iface != container_table['Other'][0]: #'eth3':
                egress_counter_other = egress_counter_other + 1
                mydb.insert_point('172.17.0.1',8086, 'POSMAC', 'cls', {"IP": forwarded_packet[IP].dst, "type": 'model'},{'accuracy': ((pkt_counter_other - egress_counter_other)/pkt_counter_other)})
                print('Other pkt percentage: ',((pkt_counter_other - egress_counter_other)/pkt_counter_other))

                    

        # Classification the packet
      
       

def main():
    global classifier, reset_time, model_path_folder, ar, cg, other
    config_file = '/home/cls/config.yaml'
    config = load_config(config_file)
    ar = config['cls_config']['servers']['AR']['ip']
    cg = config['cls_config']['servers']['CG']['ip']
    other = config['cls_config']['servers']['Other']['ip']
    # SRC_INTERFACE = config['cls_config']['ingress']['interface']  # Set Interface to listen to Pcappool
    model_path_folder = config['cls_config']['ot']['ml_file'] # folder to find the latest one
    model_path = config['cls_config']['model'][config['cls_config']['model']['selection']]['path']  # Model to start
    SRC_INTERFACE = config['cls_config']['ingress']['interface']
    reset_time = config['cls_config']['lookup_table']['reset_time']
    entry_num = config['cls_config']['lookup_table']['reset_entry_num']
    classifier = PacketClassifier(model_path)

    print('The model in this classifier is ', config['cls_config']['model']['selection'],' loaded from ', model_path)
    print(f'The reset time for lookup table [and model loading!] is {reset_time}')
    print(f'The latest model will be reloaded from {model_path_folder}')
    print('Good luck with POSMAC TC Componenent!')

    

    print(f"Listening for UDP packets on {SRC_INTERFACE}...")
    sniff(iface=SRC_INTERFACE, prn=forward_packet, store=False)
 
    print(f"Total packets received: {packets_received}")
    print(f"Total packets forwarded: {packets_forwarded}")

if __name__ == "__main__":
    main()

    #profiler = cProfile.Profile()
    #profiler.run('main()')
    #profiler.print_stats()

