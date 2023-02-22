# config and environment
import tomli
import sys, os
import sslkeylog
import pandas as pd
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['gg-photo']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GPhotosPageLoader
        
if __name__ == '__main__':
    try:
        # Read file csv and get links
        df = pd.read_csv("")
        df_link = df['Links']
        
        for i in range(len(df_link)):
            # Create timestamp

            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = './output/Photo_sslkey_{timestamp}.log'

            # Load photo
            photo = GPhotosPageLoader(df_link[i])
            photo.load(df_link[i])

            # Start capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, './output/Photo_{timestamp}.pcap')
            photo.download()

            # Turn off capture and driver
            capture.terminate()
            photo.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()