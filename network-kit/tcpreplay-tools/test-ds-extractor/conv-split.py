import os
import re

import numpy as np
import pandas as pd

import time
import subprocess

import argparse as arg
import concurrent.futures
from scapy.all import *

CONC_THREAD = 1
OUTPUT_FOLDER = '/home/hoangnv46/Documents/mininet-lab-tools/network-kit/tcpreplay-tools/test-ds-extractor/output_split'
INPUT_FOLDER = '/home/hoangnv46/Documents/mininet-lab-tools/network-kit/tcpreplay-tools/test-ds-extractor/output/NetFlow-QUIC1'

def conv_split(input_pcap):
    # Define the filter expression
    gquic_filter = "(src port 443 or dst port 443) and udp"

    # Capture GQUIC packets using the filter expression
    gquic_packets = sniff(offline=input_pcap, filter=gquic_filter)

    conversations = {}
    for packet in gquic_packets:
        src = packet[IP].src
        dst = packet[IP].dst
        key = tuple(sorted([src, dst]))
        if key in conversations:
            conversations[key].append(packet)
        else:
            conversations[key] = [packet]

    service_name = ""
    if input_pcap.find("FileTransfer") != -1:
        service_name = "FileTransfer"
    elif input_pcap.find("Google_PlayMusic") != -1:
        service_name = "Google_PlayMusic"
    elif input_pcap.find("GoogleHangout_VoIP") != -1:
        print(f"=== {len(conversations)} ===")
        service_name = "GoogleHangout_VoIP"

    # Write each conversation to a separate pcap file
    count = 0
    for key in conversations:
        origin_filename = os.path.splitext(os.path.basename(input_pcap))[0]
        directory = f'{OUTPUT_FOLDER}/{service_name}/{origin_filename}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = f'{directory}/{count}.pcap'
        wrpcap(filename, conversations[key])
        count += 1
    
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
            tasks.append(pool.submit(conv_split, item))

        for task in concurrent.futures.as_completed(tasks):
            finised_filename, result, err = task.result()
            print(finised_filename, result, err)