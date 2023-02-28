import subprocess
import os, signal

import logging

QUIC_DECODE_AS = 'udp.port==443,quic'
WEB_FILTER = '(quic and udp.port==443) or ((http or http2) or (tls.app_data and not tls.handshake) and tcp.payload and tcp.port==443 or tcp.port==80)'
class PcapCapture:
    '''
    PcapCapture is a class that uses tshark to capture packets from an interface
    and save them to a pcap file:
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
        '''
        Invoke tshark to capture packets from an interface and save them to a pcap file
        interface: The interface to capture packets from
        pcap_filename: The path to the pcap file to save the packets to
        '''
        self.pcap_filename = pcap_filename
        tshark_capture_cmd = f'tshark -i {interface} -w {self.pcap_filename}_temp'
        if self.autostop:
            tshark_capture_cmd += f' -a {self.autostop}'

        logging.info(f'Capturing packets on {interface} to {self.pcap_filename}')
        result = subprocess.Popen(tshark_capture_cmd, shell=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        result_out = result[0].decode('latin-1')
        result_err = result[1].decode('latin-1')
        logging.info(result_out)
        if result_err:
            logging.error(result_err)
        
        self._apply_filter()

    def _apply_filter(self):
        if os.path.exists(f'{self.pcap_filename}_temp'):
            tshark_filter_cmd = f'tshark -r {self.pcap_filename}_temp -w {self.pcap_filename}'
            if self.decode_as:
                tshark_filter_cmd += f' -d {self.decode_as}'
            if self.filter:
                tshark_filter_cmd += f' -Y {self.filter}'

            result = subprocess.Popen(tshark_filter_cmd, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

            os.remove(f'{self.pcap_filename}_temp')

            result_out = result[0].decode('latin-1')
            result_err = result[1].decode('latin-1')
            logging.info(result_out)
            if result_err:
                logging.error(result_err)
        else:
            logging.error(f'File {self.pcap_filename}_temp not found')

    # TODO:used on Interrupt or Exception orcurred
    def clean_up(self):
        if os.path.exists(f'{self.pcap_filename}_temp'):
            os.remove(f'{self.pcap_filename}_temp')
        if os.path.exists(f'{self.pcap_filename}'):
            os.remove(f'{self.pcap_filename}')

class AsyncPcapCapture(PcapCapture):
    def __init__(self, decode_as=None, filter=None):
        '''
            Allow asynchronous capture allow user interaction while capturing
            There can be only one capture object at a time
            Requires a call to terminate() to stop capturing
        '''
        super().__init__(decode_as, filter, None)
        self.process = None

    def capture(self, interface, pcap_filename):
        if self.process:
            logging.error('', 'Already capturing')
            return

        self.pcap_filename = pcap_filename
        tshark_capture_cmd = f'tshark -i {interface} -w {self.pcap_filename}_temp'

        # disable autostop for manual termination
        # if self.autostop:
        #     tshark_capture_cmd += '-a', self.autostop

        logging.info(f'Capturing packets on {interface} to {self.pcap_filename}')
        self.process = subprocess.Popen(tshark_capture_cmd, shell=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def terminate(self):
        if self.process:
            result = subprocess.Popen(f'pgrep -P {self.process.pid}',
                                      shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            parent_pid = int(result[0].decode('latin-1').split('\n')[0])
            os.kill(parent_pid, signal.SIGTERM)
            return_code = self.process.wait()
            self.process = None

            if return_code != 0:
                logging.error('Error in terminating process')
                return

            super()._apply_filter()
            return return_code
        else:
            logging.error('No process to terminate')

class QUICTrafficCapture(PcapCapture):
    '''
    Capture QUIC traffic on a given interface
    autostop: autostop condition
    '''
    def __init__(self, autostop='duration:10'):
        super().__init__(QUIC_DECODE_AS, 'quic',
                         autostop)

class WebTrafficCapture(PcapCapture):
    def __init__(self, autostop='duration:60'):
        super().__init__(decode_as=QUIC_DECODE_AS,
                         filter=WEB_FILTER,
                         autostop=autostop)

class AsyncQUICTrafficCapture(AsyncPcapCapture):
    def __init__(self):
        super().__init__(QUIC_DECODE_AS, 'quic')

class AsyncWebTrafficCapture(AsyncPcapCapture):
    def __init__(self):
        super().__init__(decode_as=QUIC_DECODE_AS,
                         filter=WEB_FILTER)

# class QUICAndHTTPTrafficCapture(PcapCapture):
#     def __init__(self, autostop='duration:60'):
#         super().__init__(filter='quic and tcp.payload and tcp.port==443 or http or http2 and tcp.payload and tcp.port==443 or tcp.port==80',
#                          autostop=autostop)

# class AsyncQUICAndHTTPTrafficCapture(AsyncPcapCapture):
#     def __init__(self):
#         super().__init__(filter='quic and tcp.payload and tcp.port==443 or http or http2 and tcp.payload and tcp.port==443 or tcp.port==80')