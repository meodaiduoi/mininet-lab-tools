# config and environment
import tomli
import sys, os
import sslkeylog
import pandas as pd
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['gg-docs']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GDocsPageLoader
        
if __name__ == '__main__':
    try:
        # Create timestamp

        # Save ssl key to file
        os.environ['SSLKEYLOGFILE'] = './output/Docs_sslkey_{timestamp}.log'

        # Load docs
        docs = GDocsPageLoader("")
        docs.user("account","passwrd")
        docs.signin()

        # Start capture
        capture = AsyncQUICTrafficCapture()
        capture.capture(interface, './output/Docs_{timestamp}.pcap')
        docs.editor()

        # Turn off capture and driver
        capture.terminate()
        docs.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()