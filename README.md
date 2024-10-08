# POSMAC: Powering Up In-Network AR/CG Traffic Classification with Online Learning

<table align="center">
  <tr>
    <td> <img src="https://github.com/dcomp-leris/VR-AR-CG-network-telemetry/assets/58492556/67a96a00-c791-46b3-afac-daf3ae212aeb" align="middle" alt="Leris" width="150" height="150"></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><img src="https://github.com/user-attachments/assets/8f9e55aa-cfe0-4c3d-9563-aee0601fb73d" alt="Conference" align="middle" width="350" height="150"></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td><img src="https://github.com/dcomp-leris/VR-AR-CG-network-telemetry/assets/58492556/b26a6be8-6b16-4542-bb3e-7eeac34644d6" align="middle" alt="SMARTNESS" width="150" height="150"></td>
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

### 2-1- Host computer: 
It is a computer system with Ubuntu 24.04 LTS Linux Operating System which hosts all POSMAC components (Pcap pool, TC, AR, CG, Other, and OT) which are containers.  
### 2-2- Docker: 
Install the docker on the host system for hosting the containers (https://docs.docker.com/engine/install/ubuntu/)
### 2-3- Linux-based Containers: 
For pcappool, AR, CG, Other, OT components. Pull the image on the POSMAC host.
              
              $ sudo docker pull ubuntu:24.04
### 2-4- Linux-based DOCA Container for Bluefield 3.0: 
For TC component. Pull the image on the POSMAC host.
  
              $ sudo docker pull nvcr.io/nvidia/doca/doca:2.8.0-devel

### 2-5- QEMU for Multi-Architecture (X86/arm64): [https://www.qemu.org/download/#linux]

              $ sudo apt update 
              $ apt-get install qemu-user-static

## 3- Run & Setup Containers
### 3-1- Containers Networks
              $ sudo docker network create --subnet=192.168.10.0/24 net_192_168_10
              $ sudo docker network create --subnet=192.168.20.0/24 net_192_168_20
              $ sudo docker network create --subnet=192.168.30.0/24 net_192_168_30
              $ sudo docker network create --subnet=10.10.10.0/24 net_10_10_10
              $ sudo docker network create --subnet=192.168.110.0/24 net_192_168_110
              $ sudo docker network create --subnet=192.168.120.0/24 net_192_168_120
              $ sudo docker network create --subnet=192.168.130.0/24 net_192_168_130
              $ sudo docker network create --subnet=192.168.140.0/24 net_192_168_140 
              
### 3-2- Run POSMAC Components
#### 3-2-1- Run cls container (ARM64)
    
              $ sudo docker run -dit --name cls --platform linux/arm64 --network net_192_168_10 --mac-address '02:00:00:ac:02' --ip 192.168.10.2 nvcr.io/nvidia/doca/doca:2.8.0-devel
              
***Connect additional networks (connected to cls)***

              $ sudo docker network connect  --ip 192.168.20.2 net_192_168_20 cls
              $ sudo docker network connect  --ip 192.168.30.2 net_192_168_30 cls
              $ sudo docker network connect  --ip 10.10.10.3 net_10_10_10 cls
              $ sudo docker network connect  --ip 192.168.140.2 net_192_168_140 cls

#### 3-2-2- Run TG Container (X86)
              $ docker run -dit --name TG --network net_10_10_10 --mac-address '00:00:00:00:00:01' --ip 10.10.10.2 ubuntu:latest
              
#### 3-2-3- Run ar Container (X86)
              $ docker run -dit --name ar --network net_192_168_10 --mac-address '00:00:00:00:0a:01' --ip 192.168.10.3 ubuntu:latest
              $ sudo docker network connect --ip 192.168.110.3 net_192_168_110 ar   # Connect additional networks

#### 3-2-4- Run cg Container (X86)
              $ sudo docker run -dit --name cg --network net_192_168_20 --mac-address '00:00:00:00:0b:01' --ip 192.168.20.3 ubuntu:latest
              $ sudo docker network connect --ip 192.168.120.3 net_192_168_120 cg  # Connect additional networks

#### 3-2-5- Run other Container (x86)
              $ sudo docker run -dit --name other --network net_192_168_30 --mac-address '00:00:00:00:0c:01' --ip 192.168.30.3 ubuntu:latest
              $ sudo docker network connect --ip 192.168.130.3 net_192_168_130 other # Connect additional networks

#### 3-2-6- Run ot Container (X86)
              $ sudo docker run -dit --name ot --network net_192_168_110 --mac-address '00:00:00:00:0e:01' --ip 192.168.110.2 ubuntu:latest
              $ sudo docker network connect --ip 192.168.140.3 net_192_168_140 ot  # Connect additional networks

              



  
  **3-3- Install requirements on all containers:** Python, Scapy, Joblib should be installed on all components. These softwares should be installed on all containers after running. 
  
              $ sudo apt update
              $ sudo apt install python3 python3-pip 
              $ sudo pip3 install joblib scapy
   
   
   
   
