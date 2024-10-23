# POSMAC: Powering Up In-Network AR/CG Traffic Classification with Online Learning



<table align="center">
  <tr>
    <td style="padding-right: 2000px;">
      <img src="https://github.com/dcomp-leris/VR-AR-CG-network-telemetry/assets/58492556/67a96a00-c791-46b3-afac-daf3ae212aeb" align="middle" alt="Leris" width="150" height="150">
    </td>
    <td style="padding-right: 2000px;">
      <img src="https://github.com/user-attachments/assets/8f9e55aa-cfe0-4c3d-9563-aee0601fb73d" alt="Conference" align="middle" width="350" height="150">
    </td>
    <td>
      <img src="https://github.com/dcomp-leris/VR-AR-CG-network-telemetry/assets/58492556/b26a6be8-6b16-4542-bb3e-7eeac34644d6" align="middle" alt="SMARTNESS" width="150" height="150">
    </td>
  </tr>
</table>


⚠️**This repository is in a state of development**

## 1- Introduction

In this demonstration, we showcase **POSMAC** (Platform of Optimization & Deployment of the Online Self-Trainer Model for AR/CG Traffic Classification.), a platform designed to deploy Decision Tree (DT) and Random Forest (RF) models on the NVIDIA DOCA DPU, equipped with an ARM processor, for real-time network traffic classification. Developed specifically for Augmented Reality (AR) and Cloud Gaming (CG) traffic classification, POSMAC streamlines model evaluation, and generalization while optimizing throughput to closely match line rates. The architecture and components are shown in Fig.1.

![POSMAC_Archticture](https://github.com/user-attachments/assets/28a5c7be-1a17-430e-81f1-86e7abb7fca5)

<p align="center">
  <sub>Fig.(1). POSMAC Architecture & Components </sub>
</p>

## 2- Requirements
All the requirements should be run on the host computer which POSMAC will be run:

### 2-1- Host computer 
It is a computer system with Ubuntu 24.04 LTS Linux Operating System which hosts all POSMAC components (Pcap pool, TC, AR, CG, Other, and OT) which are containers.  
### 2-2- Docker 
Install the docker on the host system for hosting the containers 

(https://docs.docker.com/engine/install/ubuntu/)

### 2-3- Linux-based Containers 
For pcappool, AR, CG, Other, OT components. Pull the image on the POSMAC host.
              
    $ sudo docker pull ubuntu:24.04

### 2-4- Linux-based DOCA Container for Bluefield 3.0 
For TC component. Pull the image on the POSMAC host.
  
    $ sudo docker pull nvcr.io/nvidia/doca/doca:2.8.0-devel

### 2-5- QEMU for Multi-Architecture (X86/arm64)

[https://www.qemu.org/download/#linux]

    $ sudo apt update 
    $ apt-get install qemu-user-static

## 3- Setup Infrastructure with Docker & Containers  
### 3-1- Networking of the Containers 

    $ sudo docker network create --subnet=192.168.10.0/24 net_192_168_10
    $ sudo docker network create --subnet=192.168.20.0/24 net_192_168_20
    $ sudo docker network create --subnet=192.168.30.0/24 net_192_168_30
    $ sudo docker network create --subnet=10.10.10.0/24 net_10_10_10
    $ sudo docker network create --subnet=192.168.110.0/24 net_192_168_110
    $ sudo docker network create --subnet=192.168.120.0/24 net_192_168_120
    $ sudo docker network create --subnet=192.168.130.0/24 net_192_168_130
    $ sudo docker network create --subnet=192.168.140.0/24 net_192_168_140 
              
### 3-2- Run POSMAC Components
#### 3-2-1- Run "TC" Componenet with container (ARM64)

    # Container name: cls (classifier)
    
    $ sudo docker run -dit --name cls --platform linux/arm64  --privileged --network net_192_168_10 --mac-address '02:00:00:ac:02' --ip 192.168.10.2 nvcr.io/nvidia/doca/doca:2.8.0-devel
              
***Connect additional networks (connected to cls)***

    $ sudo docker network connect  --ip 192.168.20.2 net_192_168_20 cls
    $ sudo docker network connect  --ip 192.168.30.2 net_192_168_30 cls
    $ sudo docker network connect  --ip 10.10.10.3 net_10_10_10 cls
    $ sudo docker network connect  --ip 192.168.140.2 net_192_168_140 cls

#### 3-2-2- Run "PCAP Pool" Component with container (X86)
    # Container name: TG (Traffic Generator)
    
    $ docker run -dit --name TG --privileged --network net_10_10_10 --mac-address '00:00:00:00:00:01' --ip 10.10.10.2 ubuntu:latest
              
#### 3-2-3- Run "APS-ar" Componenet with container (X86) 
    # Container name: ar (augmented reality)
    
    $ docker run -dit --name ar --privileged  --network net_192_168_10 --mac-address '00:00:00:00:0a:01' --ip 192.168.10.3 ubuntu:latest
    $ sudo docker network connect --ip 192.168.110.3 net_192_168_110 ar   # Connect additional networks

#### 3-2-4- Run "APS-cg" Componenet with container (X86) 
    # Container name: cg (cloud gaming)
    
    $ sudo docker run -dit --name cg --privileged --network net_192_168_20 --mac-address '00:00:00:00:0b:01' --ip 192.168.20.3 ubuntu:latest
    $ sudo docker network connect --ip 192.168.120.3 net_192_168_120 cg  # Connect additional networks

#### 3-2-5- Run "APS-other" Componenet with container (X86) 
    # Container name: other (Non-ar and Non-cg)
    
    $ sudo docker run -dit --name other --privileged --network net_192_168_30 --mac-address '00:00:00:00:0c:01' --ip 192.168.30.3 ubuntu:latest
    $ sudo docker network connect --ip 192.168.130.3 net_192_168_130 other # Connect additional networks

#### 3-2-6- Run "OT" Container Componenet with container (X86) 
    $ sudo docker run -dit --name ot --privileged --network net_192_168_110 --mac-address '00:00:00:00:0e:01' --ip 192.168.110.2 ubuntu:latest
    $ sudo docker network connect --ip 192.168.140.3 net_192_168_140 ot  # Connect additional networks

#### 3-2-7- Configure the MAC Address of NICs
##### CLS MACs    
    $ sudo exec --it cls bash    # set the MACs
    $ ifconfig eth0 down && ifconfig eth0 hw ether 00:00:00:00:ac:02 && ifconfig eth0 up # ar container
    $ ifconfig eth1 down && ifconfig eth1 hw ether 00:00:00:00:ac:03 && ifconfig eth1 up # cg container
    $ ifconfig eth2 down && ifconfig eth2 hw ether 00:00:00:00:ac:04 && ifconfig eth2 up # other container
    $ ifconfig eth3 down && ifconfig eth3 hw ether 00:00:00:00:ac:01 && ifconfig eth3 up # TG container
    $ ifconfig eth4 down && ifconfig eth4 hw ether 00:00:00:00:ac:05 && ifconfig eth4 up # OT container

##### AR MACs    
    $ sudo exec --it ar bash    # set the MACs
    $ ifconfig eth0 down && ifconfig eth0 hw ether 00:00:00:00:0a:01 && ifconfig eth0 up
    $ ifconfig eth1 down && ifconfig eth1 hw ether 00:00:00:00:0a:02 && ifconfig eth1 up

##### CG MACs    
    $ sudo exec --it cg bash    # set the MACs
    $ ifconfig eth0 down && ifconfig eth0 hw ether 00:00:00:00:0b:01 && ifconfig eth0 up
    $ ifconfig eth1 down && ifconfig eth1 hw ether 00:00:00:00:0b:02 && ifconfig eth1 up

    
##### Other MACs    
    $ sudo exec --it other bash    # set the MACs
    $ ifconfig eth0 down && ifconfig eth0 hw ether 00:00:00:00:0b:01 && ifconfig eth0 up
    $ ifconfig eth1 down && ifconfig eth1 hw ether 00:00:00:00:0b:02 && ifconfig eth1 up

    
### 3-3- Install Required Packages inside the Containers
#### 3-3-1- Required Softwares on all containers (pcappool, cls, ar, cg, other, and ot)    
    $ apt update
    $ apt install python3 python3-pip nano # all containers
    $ apt install -y tcpreplay --break-system-packages  # Only for TG 
    $ pip3 install joblib scapy pyyaml numpy scikit-learn --break-system-packages

#### 3-3-2- Transfer Modules from Host system to the containers

In the Project repository treansfer the folder to each container

    $ sudo docker cp ./cls cls:/home/
    $ sudo docker cp ./ot ot:/home/
    $ sudo docker cp ./TG TG:/home/
    $ sudo docker cp ./ar ar:/home/
    $ sudo docker cp ./cg cg:/home/
    $ sudo docker cp ./other other:/home/
## 4- Run the POSMAC Components
Follow the order in running the components: (1) cls, (2) servers (ar, cg, other), (3) ot, (4) pcap pool

#### 4-1- Run cls Component 

- Set ingress interface connected to Pcap Pool Component (e.g., eth0)

- Set interfaces connected servers (ar, cg, other) (e.g., eth1, eth2, eth3)

- Set interface connected to Online Trainer Component (e.g., eth4)
- The mac addresses have already been configured to make it easy

      # Host
      $ Sudo docker exec -it cls bash
  
      # Inside the cls container
      $ cd home/cls
      $ nano config.yaml
      $ python3 run_cls.py 
    
**Output-->** By default choos **option (3)** to enable online learning capability and classification/forwarding capability! 

   ![posmac_cls](https://github.com/user-attachments/assets/63ef5045-f71d-4e51-b4d5-b7e1ca0980b2)

#### 4-2- Run Servers Componenet

- Set ingress interface connected to cls (e.g., in config.yaml set ***listener_interface: eth1***)
- Set interface connected to Online Trainer Component (e.g., ***ot_server:interface_name: eth2***)
- The mac addresses have already been configured to make it easy
   

      # Host
      $ Sudo docker exec -it [ar/cg/other] bash
  
      # Inside the server containers which can be one of ar, cg, or other
      $ cd home/[ar/cg/other]
      $ nano config.yaml
      $ python3 run_server_agent.py
**Output-->** Server listening the Interface connected to the cls ...

![Posmac_server](https://github.com/user-attachments/assets/1cf8147e-e69e-48e8-bfa0-3babde375aa4)

  #### 4-3- Run OT Componenet

- Set OT interfaces, ports, and DT/RF models for training (Note: all have already been set!)

      # Host
      $ Sudo docker exec -it ot bash
  
      # Inside the server containers which can be one of ar, cg, or other
      $ cd home/ot
      $ nano config.yaml
      $ python3 run_ot.py
**Output-->** To use Online learning and transfering the Pre-Trained model use ***option 3***

![Posmac_ot](https://github.com/user-attachments/assets/aa02bab3-9359-4aa3-aba5-14d1b58256b6)

  #### 4-4- Run Pcap Pool Componenet

- Set interface name connected to the cls (Note: all have already been set!)

      # Host
      $ Sudo docker exec -it TG bash
  
      # Inside the server containers which can be one of ar, cg, or other
      $ cd home/pcappool
      $ nano config.yaml
      $ python3 run_pcappool.py
**Output-->** To use Online learning and transfering the Pre-Trained model use ***Option 3- Replay the PCAP files randomly (Note: The order of files replaying is random!)***

![Posmac_pcappool](https://github.com/user-attachments/assets/ca1f90e4-1747-4fd6-82aa-100eb7e85d92)

 ### 5- Monitoring

 - Go to the cls container and monitor the log!
 - use the dashboard
