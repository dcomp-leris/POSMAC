"""
Created on Sun Apr 28 22:16:09 2024
@author: alireza
Ver: 2.00 
Developed in Leris Lab
Presented in IEEE NFV-SDN 2024 Conference
"""



import socket
import threading
import yaml
import os

config_file = 'config.yaml'


def handle_client(conn, addr, output_dir):
    print(f"Connected by {addr}")
    try:
        # Generate a unique filename by checking the current count in the output directory
        file_count = len([f for f in os.listdir(output_dir) if f.startswith("ml") and f.endswith(".joblib")])
        unique_file_name = os.path.join(output_dir, f"ml{file_count + 1}.joblib")
        
        # Save the file with the unique name
        with open(unique_file_name, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)
        print(f"File {unique_file_name} received successfully from {addr}")
    finally:
        conn.close()

def receive_file(server_ip, server_port, ml_file_dir):
    # Ensure the output directory exists
    if not os.path.exists(ml_file_dir):
        os.makedirs(ml_file_dir)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server_ip, server_port))
    s.listen(5)
    print("\n")
    print(f"Listening on {server_ip}:{server_port}...")
    print(f"Files will be saved in the folder: {ml_file_dir}")

    while True:
        conn, addr = s.accept()
        # Each client connection is handled in a separate thread
        thread = threading.Thread(target=handle_client, args=(conn, addr, ml_file_dir))
        thread.start()


def load_config(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


# Example usage
if __name__ == "__main__":
    config_file = '/home/cls/config.yaml'
    config = load_config(config_file)
    srv_ip = config['cls_config']['ot']['ip']
    srv_port = config['cls_config']['ot']['port'] 
    ml_file = config['cls_config']['model'][config['cls_config']['model']['selection']]['path']  # config['cls_config']['ot']['ml_file'] # It is replaced with the place it is loading! but it can be configured separate
    ml_file2 = config['cls_config']['ot']['ml_file']             											 # location for debugging
    print("running in config is ", ml_file2)
    receive_file(f'{srv_ip}', int(srv_port), ml_file2)
    #receive_file('0.0.0.0', 5001)


