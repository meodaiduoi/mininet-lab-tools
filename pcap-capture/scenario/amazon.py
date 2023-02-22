# config and environment
import tomli
import sys, os
import sslkeylog
import pandas as pd
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['amazon']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import AmazonLoader
        
if __name__ == '__main__':
    try:
        # Read file csv and get links
        df = pd.read_csv("")
        df_link = df['Links']
        
        for i in range(len(df_link)):
            # Create timestamp

            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = './output/Amazon_sslkey_{timestamp}.log'

            # Get link
            amazon = AmazonLoader(df_link[i])

            # Start capture
            capture = AsyncHTTPTrafficCapture()
            capture.capture(interface, './output/Amazon_{timestamp}.pcap')
            amazon.load(df_link[i])

            # Turn off capture and driver
            capture.terminate()
            amazon.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()