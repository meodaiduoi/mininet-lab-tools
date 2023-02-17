from webpcap.pcapcapture import QUICTrafficCapture
from webpcap.ggservice import GDocsPageLoader
from logging import warn, error, info, debug, critical
import os, sys
import pandas as pd
import tomli

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        sys.path.insert(0, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

def main():
    docs = GDocsPageLoader("url")
    docs.user("", "")
    docs.signin()
    docs.editor()        
        
if __name__ == '__main__':
    capture = QUICTrafficCapture('ens33')
    capture.capture()
    try:
        main()
    except KeyboardInterrupt:
        error('Keyboard Inter')
        sys.exit()