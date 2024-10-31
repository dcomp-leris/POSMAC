"""
Created on Sun Apr 28 22:16:09 2024
@author: alireza
Ver: 2.00 
Developed in Leris Lab
Presented in IEEE NFV-SDN 2024 Conference
"""

import yaml
import hashlib
from scapy.all import IP, UDP, sendp, Ether, sniff, TCP
import socket
import time
import threading
import os
import subprocess
import glob
import shutil 
import readline
import yaml
import subprocess
import glob



''' Global Variable Definition '''
conf_file = 'config.yaml'
pkt_no = 0
#config = load_config()
ack_sent = {}  # Change this to a dictionary to track timestamps
config = None
ot_server_ip = ''
ot_server_port = ''
app_server_list = []
app_name = ''
####################################################################

''' Function Definition  '''

def print_header(app_name, port_to_ot, port_from_cls):
    terminal_width = shutil.get_terminal_size().columns
    header_width = terminal_width - 2  # Account for padding on both sides
    print("\n" + "*" * header_width)
    print("*" + " " * (header_width - 2) + "*")
    print("*" + " ****  ****  *****        *       *             *        *****  ".center(header_width - 2) + "*")
    print("*" + " ****  ****  *           * *     * *           ***       *   *  ".center(header_width - 2) + "*")
    print("*" + " ****  ****  *          *  *    *   *         *****      *      ".center(header_width - 2) + "*")
    print("*" + " ****  ****  *****     *    *   *    *       *******     *      ".center(header_width - 2) + "*")
    print("*" + " ****  ****      *    *      * *      *     *       *    *      ".center(header_width - 2) + "*")
    print("*" + " *     ****      *   *       ***       *   *         *   *   *  ".center(header_width - 2) + "*")
    print("*" + " *     ****  *****  *        ***        * *           *  *****  ".center(header_width - 2) + "*")

    print("*" + " " * (header_width - 2) + "*")
    print("*" + f"DEMO - Application Server for {app_name} server".center(header_width - 2) + "*")
    print("*" + f"Receives from {port_from_cls} (cls) and sends to {port_to_ot} (ot)".center(header_width - 2) + "*")
    print("*" + "APS Module Ver.2.00 2024/11/06".center(header_width - 2) + "*")
    print("*" + "Developed by: LERIS Lab (UFSCar) ".center(header_width - 2) + "*")
    print("*" + "Supported by: Ericsson Telecomunication Ltda, FAPESP, and CPE SMARTNESS ".center(header_width - 2) + "*")
    print("*" + "Presented in IEEE NFV-SDN 2024 Conference ".center(header_width - 2) + "*")
    #print("*" + "APS Module Ver.1.00 2204/05/09 (Exit --> ctl+c)".center(header_width - 2) + "*")
    #print("*" + "LERIS Lab (UFSCar) ".center(header_width - 2) + "*")
    print("*" + " " * (header_width - 2) + "*")
    print("*" * header_width + "\n")




def load_config(conf_addr):
    with open(conf_addr, 'r') as file:
        return yaml.safe_load(file)

def cleanup_ack_sent(reset_time):
    while True:
        current_time = time.time()
        keys_to_remove = [key for key, val in ack_sent.items() if (current_time - val) > reset_time]  # 1 second = 1000 ms
        for key in keys_to_remove:
            del ack_sent[key]
        time.sleep(reset_time/10)  # x 1000 will be time in ms e.g. when reset_time is 1 then check time will be 0.1 that means it Checks every 100 ms

def match_and_forward(packet):
    global pkt_no
    if IP in packet and UDP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
        packet_size = len(packet)
        pkt_no += 1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{pkt_no}: {timestamp}] Packet Received: Src IP: {src_ip}, Dst IP: {dst_ip}, SRC Port: {src_port} ,Dst Port: {dst_port}, Size: {packet_size} bytes")

        for match in app_server_list: #config['appserver_config']['ar_servers']:
            if src_ip == match['src_ip'] and dst_ip == match['dst_ip'] and dst_port == match['port']:
                message = [f'Ack from {app_name} Server:', (src_ip, dst_ip, src_port, dst_port), str(app_name)]
                send_to_ml_server(message)
            elif dst_ip == match['dst_ip']: ## it was added to extend the destination ip address control
                message = [f'ACK from {app_name} Server:', (src_ip, dst_ip, src_port, dst_port), str(app_name)]
                send_to_ml_server(message)

def send_to_ml_server(message):
    #server_config = config['appserver_config']['ot_server']
    if message[1] not in ack_sent:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(str(message).encode(),(ot_server_ip,ot_server_port))  #(config['appserver_config']['ot_server']['ip'], config['appserver_config']['ot_server']['port']))
            ack_sent[message[1]] = time.time()  # Save timestamp
            print(f"Sent to server {message}!!!!!!!!!!!!!!!!!!!!!!")

def main():
    global config, ot_server_ip, ot_server_port, app_server_list, app_name
    config = load_config(conf_file)
    ot_server_ip = config['appserver_config']['ot_server']['ip']
    ot_server_port = config['appserver_config']['ot_server']['port']
    reset_time =  config['appserver_config']['reset']['flw_reset_time']
    app_server_list = config['appserver_config']['app_servers']
    app_name = config['appserver_config']['app']['name']
    
    print_header(app_name, str((ot_server_ip, ot_server_port)) ,config['appserver_config']['listener_interface'])
    cleanup_thread = threading.Thread(target=cleanup_ack_sent,args=(int(reset_time),), daemon=True)
    cleanup_thread.start()
    print(f"Listening for packets on {config['appserver_config']['listener_interface']}...")
    sniff(iface=config['appserver_config']['listener_interface'], prn=match_and_forward,store=False)



if __name__ == "__main__":
    main()






