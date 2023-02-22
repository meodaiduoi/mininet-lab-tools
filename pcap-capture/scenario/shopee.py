# config and environment
import tomli
import sys, os
import sslkeylog
import pandas as pd
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['shopee']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import ShopeeLoader
        
if __name__ == '__main__':
    try:
        # Read file csv and get links
        df = pd.read_csv("")
        df_link = df['Links']
        
        for i in range(len(df_link)):
            # Create timestamp

            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = './output/Shopee_sslkey_{timestamp}.log'

            # Get link
            shopee = ShopeeLoader(df_link[i])

            # Start capture
            capture = AsyncQUICAndHTTPTrafficCapture()
            capture.capture(interface, './output/Shopee_{timestamp}.pcap')
            shopee.load(df_link[i])

            # Turn off capture and driver
            capture.terminate()
            shopee.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()