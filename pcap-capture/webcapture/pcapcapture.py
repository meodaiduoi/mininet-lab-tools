import subprocess
import os, sys
import time

import logging

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
    def __init__(self, decode_as=None, 
                 filter=None, autostop='duration:5'):

        self.autostop = autostop
        self.filter = filter
        self.decode_as = decode_as
        self.autostop = autostop
            
    def capture(self, interface, pcap_filename):
        self.pcap_filename = pcap_filename
        tshark_capture_cmd = f'tshark -i {interface} -w {self.pcap_filename}_temp'
        if self.autostop:
            tshark_capture_cmd += f' -a {self.autostop}'

        logging.info(f'Capturing packets on {interface} to {self.pcap_filename}')
        result = subprocess.Popen(tshark_capture_cmd, shell=False,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        logging.info(result[0].decode('latin-1'), result[1].decode('latin-1'))
        self.__apply_filter()


    def __apply_filter(self):
        if os.path.exists(f'{self.pcap_filename}_temp'):
            tshark_filter_cmd = f'tshark -r {self.pcap_filename}_temp -w {self.pcap_filename}'
            if self.decode_as:
                tshark_filter_cmd += f' -d {self.decode_as}'
            if self.filter:
                tshark_filter_cmd += f' -Y {self.filter}'

            result = subprocess.Popen(tshark_filter_cmd, shell=False,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            
            os.remove(f'{self.pcap_filename}_temp')
            logging.info(result[0].decode('latin-1'), result[1].decode('latin-1'))
        else:
            logging.error('', 'File not found')

class AsynCapCapture(PcapCapture):
    def __init__(self, decode_as=None, 
                 filter=None, autostop=None):
        super().__init__(decode_as, filter, autostop)
        self.process = None
    
    def capture(self, interface, pcap_filename):
        self.pcap_filename = pcap_filename
        tshark_capture_cmd = f'tshark -i {interface} -w {self.pcap_filename}_temp'
        if self.autostop:
            tshark_capture_cmd += '-a', self.autostop

        logging.info(f'Capturing packets on {interface} to {self.pcap_filename}')
        self.process = subprocess.Popen(tshark_capture_cmd, shell=False,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def terminate(self):
        if self.process:
            self.process.send_signal(15) # 15 is SIGTERM
            return_code = self.process.wait()
            self.process = None
            self.__apply_filter()
            return return_code
        else:
            logging.error('', 'No process to terminate')


class QUICTrafficCapture(PcapCapture):
    '''
    Capture QUIC traffic on a given interface
    interface: interface name
    tls_key_filename: path to the file where the TLS key will be stored
    autostop: autostop condition
    '''
    def __init__(self, interface, pcap_filename=f'quic_{time.time_ns()}.pcap', 
                 autostop='duration:60'):

        super().__init__(interface, pcap_filename,
                         'udp.port==443,quic', 'quic', autostop)

class HTTPTrafficCapture(PcapCapture):
    def __init__(self, interface, pcap_filename=f'http_{time.time_ns()}.pcap',
                       autostop='duration:60'):
        super().__init__(interface, pcap_filename,
                         'http or http2 and tcp.payload and tcp.port==443 or tcp.port==80',
                         autostop)

class AsycnQUICTrafficCapture(AsynCapCapture):
    def __init__(self, interface, pcap_filename=f'quic_{time.time_ns()}.pcap',
                       autostop=None):

        super().__init__(interface, pcap_filename,
                         'udp.port=443,quic', 'quic', autostop)

class AsycnHTTPTrafficCapture(AsynCapCapture):
    def __init__(self, interface, pcap_filename=f'http_{time.time_ns()}.pcap',
                       autostop=None):
        super().__init__(interface, pcap_filename,
                         'http or http2 and tcp.payload and tcp.port==443 or tcp.port==80',
                         autostop)

# class QUICAndHTTPTrafficCapture(PcapCapture):
#     def __init__(self, interface, pcap_filename=f'quic_http_{time.time_ns()}.pcap',
#                        tls_key_filename=f'quic_http_tls_key_{time.time_ns()}.key', autostop='duration:60'):
#         super().__init__(interface, pcap_filename, tls_key_filename,
#                          'quic and tcp.payload and tcp.port==443 or http or http2 and tcp.payload and tcp.port==443 or tcp.port==80', autostop)