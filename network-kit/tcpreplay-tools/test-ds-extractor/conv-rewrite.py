import os
import re

import numpy as np
import pandas as pd

import time
import subprocess

import argparse as arg
import concurrent.futures
from scapy.all import *

CONC_THREAD = 12
INPUT_FOLDER = '/home/hoangnv46/Documents/mininet-lab-tools/network-kit/tcpreplay-tools/test-ds-extractor/output_split'
OUTPUT_FOLDER = '/home/hoangnv46/Documents/mininet-lab-tools/network-kit/tcpreplay-tools/test-ds-extractor/output_rewrite'

hosts = ["h1", "h3", "h4", "h5", "h8"]  
servers = ["h-11-FileTransfer", "h-12-FileTransfer", "h-14-Music", "h-16-Music", "h-17-VoIP", "h-18-VoIP", "h-19-Youtube", "h-20-Youtube"]
pairs = []

for host in hosts:
    for server in servers:
        name = f'{host}-{server.split("-")[0]}{server.split("-")[1]}'
        ip_1 = f'10.0.0.{host[1:]}'
        ip_2 = f'10.0.0.{server.split("-")[1]}'
        mac_1 = f'00:00:00:00:00:{host[1:]}'
        mac_2 = f'00:00:00:00:00:{server.split("-")[1]}'
        label = f'{server.split("-")[2]}'
        pair = {"name": name, "new_ip_1": ip_1, "new_mac_1": mac_1, "new_ip_2": ip_2, "new_mac_2": mac_2, "label": label}
        pairs.append(pair)

def conv_rewrite(input_pcap):
    packets = rdpcap(input_pcap)
    old_ip = packets[0][IP].src
    old_mac = packets[0].src
    for item in pairs:
        print(f"item {item}")
        if (input_pcap.find(item['label']) != -1):
            for packet in packets:
                packet.src, packet.dst = (item['new_mac_1'], item['new_mac_2']) if packet.src == old_mac else (item['new_mac_2'], item['new_mac_1'])
                packet[IP].src, packet[IP].dst = (item['new_ip_1'], item['new_ip_2']) if packet[IP].src == old_ip else (item['new_ip_2'], item['new_ip_1'])

            dir_path = os.path.dirname(input_pcap)
            filename = os.path.basename(input_pcap)
            temp_path = dir_path.replace("output_split", "output_rewrite")
            directory = f"{temp_path}/{item['name']}"
            if not os.path.exists(directory):
                os.makedirs(directory)
            output_pcap = f'{directory}/{filename}'
            wrpcap(output_pcap, packets)

def ls_subfolders(rootdir):
    sub_folders_n_files = []
    for path, _, files in os.walk(rootdir):
        for name in files:
            sub_folders_n_files.append(os.path.join(path, name))
    return sorted(sub_folders_n_files)

if __name__ == "__main__":
    tasks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONC_THREAD) as pool:
        for item in ls_subfolders(INPUT_FOLDER):
            tasks.append(pool.submit(conv_rewrite, item))

        # for task in concurrent.futures.as_completed(tasks):
        #     finised_filename, result, err = task.result()
        #     print(finised_filename, result, err)
