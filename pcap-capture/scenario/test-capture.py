# config and environment
import tomli
import sys, os
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        sys.path.insert(0, '/home/onos/Documents/Github/mininet-lab-tools/pcap-capture/webpcap' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webpcap.pcapcapture import QUICTrafficCapture

if __name__ == '__main__':
    capture = QUICTrafficCapture('ens33')
    capture.capture()