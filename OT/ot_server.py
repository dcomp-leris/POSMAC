import socket
import threading
import sqlite3
import yaml
import os

conf_file = 'config.yaml' 
ports = []
db_name = 'traffic.db'
app_ports = []
cls_port = 12348

def load_config(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def db_insert(data):
    conn = sqlite3.connect(db_name) # 'traffic.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO traffic_data (src_ip, dst_ip, src_port, dst_port, ifi, ipi, fs, ps, class, approvals) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    ''', data)
    conn.commit()
    conn.close()

def db_update_approval(data, conditions, class_check):
    conn = sqlite3.connect(db_name) # 'traffic.db')
    cursor = conn.cursor()
    query = f'''
        UPDATE traffic_data 
        SET approvals = approvals + 1
        WHERE src_ip = ? AND dst_ip = ? AND src_port = ?  AND dst_port = ? AND class IN ({class_check})
    '''
    cursor.execute(query, (*conditions,))
    conn.commit()
    conn.close()

def listen_on_port(server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((server_ip, server_port))
        print("\n")
        print(f"Listening on {server_ip}:{server_port} for messages...")

        while True:
            message, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            message_data = eval(message.decode())  # Convert the string back to Python data structure
            #print('cls_ port is:',message_data[2])

            if server_port == 12348: #cls_port: #== 12348:
                #print('The ==================>', message_data[0][3])
                data_tuple = (message_data[0][0], message_data[0][1], message_data[0][2], message_data[0][3],
                              message_data[1][0], message_data[1][1], message_data[1][2],message_data[1][3],
                              message_data[2], 0)  # approvals set to 0 by default
                db_insert(data_tuple)

            elif server_port in app_ports: #[12345, 12346, 12347]:
                if message_data[2] == 'AR':
                    class_check = "'AR_DL', 'AR_UL', 'AR'"
                elif message_data[2] == 'CG':
                    class_check = "'CG_DL', 'CG_UL', 'CG'"
                elif message_data[2] == 'Other':
                    class_check = "'Other', 'other'"
                else:
                    class_check = "'other', 'Other'"

                db_update_approval(message_data[1][:3], conditions=(message_data[1][0], message_data[1][1],message_data[1][2] ,message_data[1][3]), class_check=class_check)

            print(f"Received from {addr} on port {server_port}: {message_data}")

def main():
    global ports, cls_port, app_ports
    #module_location = os.path.dirname(os.path.abspath(__file__))
    #load_config= module_location + '/config.yaml'
    #print(load_config)
    config = load_config(conf_file)
    server_ip = "0.0.0.0"  #config['ot_config']['cls']['ip']  #"0.0.0.0"  # Listen on all interfaces
    ports = config['ot_config']['listening']['ports']      #[12345, 12346, 12347, 12348]  # List of ports to listen on
    db_name = config['ot_config']['db']['name']
    cls_port = config['ot_config']['cls']['port']
    app_ports = config['ot_config']['listening']['app_ports']  

    threads = []
    for port in ports:
        thread = threading.Thread(target=listen_on_port, args=(server_ip, port))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()  # Optionally, wait for all threads to complete (though they run indefinitely)

if __name__ == "__main__":
    main()








