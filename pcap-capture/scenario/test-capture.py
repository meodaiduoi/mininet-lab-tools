# config and environment
import tomli
import sys, os
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        inteface = config['test-capture']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webpcap.pcapcapture import QUICTrafficCapture

if __name__ == '__main__':
    print('a')
    capture = QUICTrafficCapture(interface=inteface, pcap_filename='./test.pcap',autostop='duration:3')
    result = capture.capture()
    print(result)