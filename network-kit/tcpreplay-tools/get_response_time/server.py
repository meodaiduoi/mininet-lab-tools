from scapy.all import *
import requests as rq

# Set the IP address and port to listen on
ip = "0.0.0.0"

# Define a callback function to handle incoming packets
def handle_packet(packet):
    if IP in packet:
        print(f"hit")
        # Create a new IP packet with the source and destination IP addresses reversed
        ip_pkt = IP(src=packet[IP].dst, dst=packet[IP].src)

        # Create a new ICMP ping reply packet
        icmp_pkt = ICMP(type=0, code=0)

        # Combine the IP and ICMP packets and send them back to the client
        reply_pkt = ip_pkt / icmp_pkt
        send(reply_pkt)

# Start a scapy sniffing session to listen for incoming packets
sniff(filter=f"src {ip}", count=5, prn=handle_packet)