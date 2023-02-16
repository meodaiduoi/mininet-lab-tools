import subprocess
import os, sys
import time

class PcapCapture:
    '''
    PcapCapture is a class that uses tshark to capture packets from an interface
    and save them to a pcap file:
    interface: The interface to capture packets from
    pcap_filename: The path to the pcap file to save the packets to
    tls_key_filename: The path to the file to save the TLS key to
    decode_as: A string of the format "tcp.port==443,http" to decode packets
    filter: A string of the format to filter packets
    autostop: A string of the format "duration:60" to stop capturing after 60 seconds
    '''
    def __init__(self, interface, pcap_filename, tls_key_filename,
                 decode_as=None, filter=None, autostop='duration:60'):

        self.tshark_command = ['tshark']
        if decode_as:
            self.tshark_command += ['-d', decode_as]
        if filter:
            self.tshark_command += ['-Y', filter]
        if autostop:
            self.tshark_command += ['-a', autostop]

        self.tshark_command = [
            '-i', interface,
            '-o', f'ssl.keylog_file:{tls_key_filename}',
            '-w', pcap_filename
        ]

    def capture(self):
        result = subprocess.Popen(self.tshark_command, shell=False,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        return (result[0].decode('latin-1'), result[1].decode('latin-1'))

# Usage
# capture = PcapCapture("eth0", "/path/to/tls.key", "/path/to/capture.pcap")
# capture.

class AsynCapCapture(PcapCapture):
    def capture(self):
        self.process = subprocess.Popen(self.tshark_command, shell=False,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def terminate(self):
        self.process.terminate()

class QUICTrafficCapture(PcapCapture):
    '''
    Capture QUIC traffic on a given interface
    interface: interface name
    tls_key_filename: path to the file where the TLS key will be stored
    autostop: autostop condition
    '''
    def __init__(self, interface, pcap_filename=f'quic_{time.time_ns()}.pcap',
                       tls_key_filename=f'quic_tls_key_{time.time_ns()}.key',
                       autostop='duration:60'):

        super().__init__(interface, pcap_filename, tls_key_filename,
                         'udp.port=443,quic', 'quic', autostop)

class HTTPTrafficCapture(PcapCapture):
    def __init__(self, interface, pcap_filename=f'http_{time.time_ns()}.pcap',
                       tls_key_filename=f'http_tls_key_{time.time_ns()}.key', autostop='duration:60'):
        super().__init__(interface, pcap_filename, tls_key_filename,
                         'http or http2 and tcp.payload and tcp.port==443 or tcp.port==80',
                         autostop)

class AsycnQUICTrafficCapture(AsynCapCapture):
    def __init__(self, interface, pcap_filename=f'quic_{time.time_ns()}.pcap',
                       tls_key_filename=f'quic_tls_key_{time.time_ns()}.key',
                       autostop='duration:60'):

        super().__init__(interface, pcap_filename, tls_key_filename,
                         'udp.port=443,quic', 'quic', autostop)

class AsycnHTTPTrafficCapture(AsynCapCapture):
    def __init__(self, interface, pcap_filename=f'http_{time.time_ns()}.pcap',
                       tls_key_filename=f'http_tls_key_{time.time_ns()}.key', autostop='duration:60'):
        super().__init__(interface, pcap_filename, tls_key_filename,
                         'http or http2 and tcp.payload and tcp.port==443 or tcp.port==80',
                         autostop)

# class QUICAndHTTPTrafficCapture(PcapCapture):
#     def __init__(self, interface, pcap_filename=f'quic_http_{time.time_ns()}.pcap',
#                        tls_key_filename=f'quic_http_tls_key_{time.time_ns()}.key', autostop='duration:60'):
#         super().__init__(interface, pcap_filename, tls_key_filename,
#                          'quic and tcp.payload and tcp.port==443 or http or http2 and tcp.payload and tcp.port==443 or tcp.port==80', autostop)