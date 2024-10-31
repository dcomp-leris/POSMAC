"""
Created on Sun Apr 28 22:16:09 2024
@author: alireza
Ver: 2.00 
Developed in Leris Lab
Presented in IEEE NFV-SDN 2024 Conference
"""

# Import Required Module
import os, subprocess, glob, shutil, readline, yaml
#subprocess, glob, shutil, readline, yaml


# Auto Complete Command Line
def setup_readline():
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(' \t\n=')

# Load yaml file Config
def load_config(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Print Header
def print_header():
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
    print("*" + "DEMO - Network Traffic Replay".center(header_width - 2) + "*")
    print("*" + "PCAP Pool Ver.2.00 2204/11/06".center(header_width - 2) + "*")
    print("*" + "Developed by: LERIS Lab (UFSCar) ".center(header_width - 2) + "*")
    print("*" + "Supported by: Ericsson Telecomunica Ltda, FAPESP, and CPE SMARTNESS ".center(header_width - 2) + "*")
    print("*" + "Presented in IEEE NFV-SDN 2024 Conference ".center(header_width - 2) + "*")
    print("*" + " " * (header_width - 2) + "*")
    print("*" * header_width + "\n")



def main_menu():
    print_header()
    setup_readline()

    module_location = os.path.dirname(os.path.abspath(__file__))

    config_file = input(f"Please enter the [config.yaml] file address: [{module_location}] ")
    pcap_folder = input("Please enter the folder address includes pcap files [PCAP files]: ")
    config = load_config(config_file)
    
    while True:
        print("\nMain Menu:")
        print("1- Modify the PCAP Files [Change the Src & Dst Address] (Note: One time is necessary!)")
        print("2- Modify Destination IP address in PCAP files (Note: Accordance with file name [AR_, CG_, other_])")
        print("3- Replay the PCAP files randomly (Note: The order of files replaying is random!)")
        print("4- Change the Pcap files' folder address [After Modification!]")
        print("5- Change the Config file address [config.yaml]")
        print("6- Exit")

        choice = input("Enter the number of the menu option: ")
        modified_folder = os.path.join(pcap_folder, "modified")
        if choice == '1':
            modify_pcap_files(pcap_folder, config)
        elif choice == '2':
            modify_destination_ip(pcap_folder, config)
        elif choice == '3':
            replay_submenu(pcap_folder, config)
        elif choice == '4':
            pcap_folder = input("Please enter the folder address includes pcap files [PCAP files]: ")
        elif choice == '5':
            config_file = input(f"Please enter the [config.yaml] file address: [{module_location}] ")
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a valid menu option.")

def modify_pcap_files(pcap_folder, config):
    # Your existing code for modifying PCAP files can be placed here
    modified_folder = os.path.join(pcap_folder, "modified")
    #modified_folder = os.path.join(pcap_folder, "modified")
    if not os.path.exists(modified_folder):
        os.makedirs(modified_folder)

    for pcap_file in glob.glob(os.path.join(pcap_folder, '*.pcap*')):
            if not pcap_file.startswith(modified_folder):
                outfile = os.path.join(modified_folder, os.path.basename(pcap_file))
                command = ['tcprewrite', '--infile', pcap_file, '--outfile', outfile,
                           '--enet-smac', config['traffic_config']['mac_addresses']['srcMAC'],
                           '--enet-dmac', config['traffic_config']['mac_addresses']['dstMAC']]

                subprocess.run(command, check=True)
                print(f"Processed {pcap_file} and saved as {outfile}")
                print(f"Note--> Please return to main menu and change the replay pcap folder to the modified folder!")

    #pass

def modify_destination_ip(pcap_folder, config):
    # Your existing code for modifying destination IP can be placed here
    modified_folder = os.path.join(pcap_folder, "modified")
    if not os.path.exists(modified_folder):
        os.makedirs(modified_folder)

    #modified_folder = os.path.join(pcap_folder, "modified")
    for pcap_file in glob.glob(os.path.join(pcap_folder, '*.pcap*')):
            if not pcap_file.startswith(modified_folder):
                outfile = os.path.join(modified_folder, os.path.basename(pcap_file))
                command = ['tcprewrite', '--infile', pcap_file, '--outfile', outfile,
                           '--enet-smac', config['traffic_config']['mac_addresses']['srcMAC'],
                           '--enet-dmac', config['traffic_config']['mac_addresses']['dstMAC']]

                
                if 'AR_' in os.path.basename(pcap_file):
                    new_ip = config['traffic_config']['ip_addresses']['AR_IP']
                elif 'CG_' in os.path.basename(pcap_file):
                    new_ip = config['traffic_config']['ip_addresses']['CG_IP']
                elif 'other_' in os.path.basename(pcap_file):
                    new_ip = config['traffic_config']['ip_addresses']['Other_IP']
                else:
                    new_ip = None

                if new_ip:
                    command.extend(['--dstipmap', f"0.0.0.0/0:{new_ip}"])
                    '''command = ['tcprewrite', '--infile', pcap_file, '--outfile', outfile,
                           '--enet-smac', config['traffic_config']['mac_addresses']['srcMAC'],
                           '--enet-dmac', config['traffic_config']['mac_addresses']['dstMAC'],'--dstipmap', f"0.0.0.0/0:{new_ip}"]



               command = ['tcprewrite', '--infile', pcap_file, '--outfile', outfile,
                           '--enet-smac', config['traffic_config']['mac_addresses']['srcMAC'],
                           '--enet-dmac', config['traffic_config']['mac_addresses']['dstMAC']]

                if change_ips:
                    if 'AR_' in os.path.basename(pcap_file):
                        new_ip = config['traffic_config']['ip_addresses']['AR_IP']
                    elif 'CG_' in os.path.basename(pcap_file):
                        new_ip = config['traffic_config']['ip_addresses']['CG_IP']
                    elif 'other_' in os.path.basename(pcap_file):
                        new_ip = config['traffic_config']['ip_addresses']['Other_IP']
                    else:
                        new_ip = None

                    if new_ip:
                        command.extend(['--dstipmap', f"0.0.0.0/0:{new_ip}"])'''

                #subprocess.run(command, check=True)




                subprocess.run(command, check=True)
                print(f"Processed {pcap_file} and saved as {outfile}")

    #pass

def replay_submenu(pcap_folder, config):
    while True:
        print("\nReplay Submenu:")
        print("1- Replay the PCAP files with specific as highest as possible (-t)")
        print("2- Replay the PCAP with specific ppk/second (-P)")
        print("3- Replay the PCAP with specific netowk speed (-M)")
        print("4- Back to Main Menu")

        choice = input("Enter the number of the submenu option: ")
        modified_folder = os.path.join(pcap_folder, "modified")
        if choice == '1':
            # Code for replaying PCAP files with specific timing
            for pcap_file in glob.glob(os.path.join(pcap_folder, '*.pcap*')):
                if not pcap_file.startswith(modified_folder):  # Ensure we do not replay modified files
                    print(f"Replaying {os.path.basename(pcap_file)} on {config['traffic_config']['interface']}...")
                    command = ['tcpreplay', '--intf1', config['traffic_config']['interface'],'-t','-K', pcap_file]
                    subprocess.run(command, check=True)
                    print(f"Successfully replayed {pcap_file}.")

        elif choice == '2':
            for pcap_file in glob.glob(os.path.join(pcap_folder, '*.pcap*')):
                if not pcap_file.startswith(modified_folder):  # Ensure we do not replay modified files
                    print(f"Replaying {os.path.basename(pcap_file)} on {config['traffic_config']['interface']}...")
                    command = ['tcpreplay', '--intf1', config['traffic_config']['interface'],'--pps', str(config['traffic_config']['replay']['pps']) ,'-K', pcap_file]
                    subprocess.run(command, check=True)
                    print(f"Successfully replayed {pcap_file}.")

            # Code for replaying PCAP files with specific packets per second
            pass
        elif choice == '3':
            for pcap_file in glob.glob(os.path.join(pcap_folder, '*.pcap*')):
                if not pcap_file.startswith(modified_folder):  # Ensure we do not replay modified files
                    print(f"Replaying {os.path.basename(pcap_file)} on {config['traffic_config']['interface']}...")
                    command = ['tcpreplay', '--intf1', config['traffic_config']['interface'],'--mbps', str(config['traffic_config']['replay']['speed']) ,'-K', pcap_file]
                    subprocess.run(command, check=True)
                    print(f"Successfully replayed {pcap_file}.")

        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a valid submenu option.")

if __name__ == "__main__":
    main_menu()
