import subprocess
import time
from scapy.all import *

# Set the path to the PCAP file and the interface to send packets out on
pcap_file = "./h14-h9-udp.pcap"
interface = "eth0"

# Set the target IP and MAC addresses
src_ip = "172.10.0.14"
target_ip = "172.10.0.9"
target_mac = "02:42:ac:0a:00:09"

packets = rdpcap(pcap_file)

# Open the PCAP file and iterate over the packets
with open("response_times.txt", "w") as f:
    for packet in packets:
        print(packet)
        # Check if the packet is an Ethernet packet with the target MAC address
        if Ether in packet and packet[Ether].dst == target_mac:
            # Check if the packet is an IP packet with the target IP address
            if IP in packet and packet[IP].dst == target_ip and packet[IP].src == src_ip:
                # Rewrite the Ethernet header with the interface's MAC address
                packet[Ether].src = get_if_hwaddr(interface)
                start_time = time.time()
                sendp(packet, iface=interface)
                print("sent")
                # Use scapy.sniff() to receive the response packet and record the end time
                sniff(count=1, filter=f"icmp")
                print("test")
                end_time = time.time()

                # Calculate the total time and log it
                total_time = end_time - start_time
                f.write(f"Response time: {total_time:.2f} ms\n")