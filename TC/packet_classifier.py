#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 22:16:09 2024

@author: alireza
Ver: 2.00 
Date: 2024-10-25
"""

from scapy.all import sniff, IP, UDP
import time
import numpy as np
from joblib import load
#from custom_model import CustomDecisionTreeModel
import warnings
import hashlib

warnings.filterwarnings('ignore', category=UserWarning)

# model_path = "dt_model.joblib"
# model_path = "./mymodel/dt.joblib"


class PacketClassifier:
    def __init__(self, model_path):
        self.model = load(model_path)
        self.flow_features = {}
        print(model_path)
        #self.hasher = hashlib.sha256()
        #self.flow_packet_count = {}  # Tracks number of packets per flow
        #self.flow_start_time = {}  # Tracks the start time of the first packet in a flow


    def update_features(self, packet, flow_key):
        		
        current_time = time.time()
        packet_size = len(packet)
        udp_payload = bytes(packet[UDP].payload)
        features = self.flow_features[flow_key]  # Use self to access instance variable

        ipi = current_time - features['last_packet_time']
        features['last_packet_time'] = current_time
        features['PS'].append(packet_size)
        features['IPI'].append(ipi)
        my_p = ''
        if len(udp_payload) >= 12:
            marker_bit = udp_payload[1] >> 7
            features['accumulated_frame_size'] += packet_size

            if marker_bit:
                fs = features['accumulated_frame_size']
                ifi = current_time - features['last_frame_start_time'] if features['last_frame_start_time'] else 0
                features['last_frame_start_time'] = current_time
                features['accumulated_frame_size'] = 0

                features['FS'].append(fs)
                features['IFI'].append(ifi)

                if len(features['FS']) >= 3 and len(features['IFI']) >= 3:
                    #print("Triggering the prediction!")
                    my_p = self.make_prediction(features, flow_key)  # Use self to refer to instance method
                    #print('return value-->',flow_key,my_p)
                    #print('classifier class',[flow_key,my_p])
                    return  [flow_key, my_p[0],my_p[1]]
                else:
                    [flow_key, None]
        else:
            return [flow_key, None]             
        #print('test ------->',flow_key,my_p)
        #return [flow_key, my_p]
        #return [flow_key, my_p] if my_p else None
	



    def make_prediction(self, features, flow_key):
        try:
            fs_average = np.average(features['FS'])         #*9
            ifi_average = np.average(features['IFI'])       #/9
            ipi_average = np.average(features['IPI'])       #/9
            ps_average = np.average(features['PS'])
            model_input = np.array([[ifi_average, ipi_average, fs_average, ps_average]])  # order is : (ifi, ipi, fs, ps)
            #model_input = np.array([[ifi_average, ipi_average, fs_average]]) # For old model
            prediction = self.model.predict(model_input)    # Use self to refer to instance variable
            #print('Input Correct::',model_input,prediction,type(prediction),prediction[0],type(prediction[0]))
            self.flow_features[flow_key]['class'] = prediction[0]
            #prediction_value = prediction[0] if prediction.size > 0 else None
            #print(f'{flow_key},{ifi_average},{ipi_average},{fs_average},{prediction[0]}') 
            #print('=====================================================================================================')
            return [prediction[0],(ifi_average,ipi_average,fs_average,ps_average)]
        except Exception as e:
            print(f"Prediction error: {e}")
            #print('Input with Error:',model_input)
            return prediction[0]


    def classify_packet(self, packet):
        # This is a simplified method to classify a single packet and return the class
        flow_key = hashlib.sha256(str((packet[IP].src, packet[IP].dst, packet[UDP].dport)).encode().hex().encode()).hexdigest()
        #flow_key = str((packet[IP].src, packet[IP].dst, packet[UDP].dport)).encode().hex() #self.hasher.hexdigest()
        #print(model_path)
 
        if flow_key not in self.flow_features:
            self.flow_features[flow_key] = {'PS': [], 'IPI': [], 'FS': [], 'IFI': [], 'last_packet_time': time.time(), 'last_frame_start_time': None, 'accumulated_frame_size': 0, 'class':'None'}
            #self.flow_start_time[flow_key] = time.time()  # Initialize start time
            #self.flow_packet_count[flow_key] = 0
        #elif  self.flow_features[flow_key]['class'] in ('AR_DL','AR_UL','CG_DL','CG_UL','Other'):
            #return (flow_key,flow_key,self.flow_features[flow_key]['class'])
        #self.flow_packet_count[flow_key] += 1
        #else:
            #print(flow_key)
            #self.update_features(packet, flow_key)   
 
        else:
            result = self.update_features(packet, flow_key)
            #print('result:',result)
            if result != None and len(result)==3: #result and isinstance(result, list):
                key, pr, myfeature = result
                return [key , pr , myfeature]
            else:
                return [flow_key, None] 
        #return self.update_features(packet, flow_key)
        # Optionally, return the prediction or flow key


