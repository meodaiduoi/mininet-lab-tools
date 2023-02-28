# config and environment
import tomli
import sys, os
import pandas as pd
import time
import logging

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        url_list = config['tiktok']['url_list']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import TiktokLoader
from webcapture.utils import *
        
if __name__ == '__main__':
    try:
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):

            # Create folder to store output
            pcapstore_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Tiktok')
            sslkeylog_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Tiktok', 'SSLKEYLOG')
            mkdir_by_path(pcapstore_path)
            mkdir_by_path(sslkeylog_path)

            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Init driver and capture object
            tiktok = TiktokLoader()
            capture = AsyncWebTrafficCapture()

            # Load tiktok page and start capture
            capture.capture(interface, f'{file_path}.pcap')
            tiktok.load(url)

            # Turn off capture and driver
            capture.terminate()
            tiktok.close_driver()

    except KeyboardInterrupt:
        tiktok.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error('Keyboard Interrupt')
        sys.exit(0)

    except Exception as e:
        tiktok.close_driver()
        capture.terminate()
        capture.clean_up()
        raise e