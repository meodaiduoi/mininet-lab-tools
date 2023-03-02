# config and environment
import tomli
import sys, os
import time
import logging
import pandas as pd

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        log_level = config['enviroment']['log_level']
        url_list = config['shopee']['url_list']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import ShopeeLoader
from webcapture.utils import *        

if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Shopee') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Shopee', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        logging.basicConfig(filename=os.path.join(pcapstore_path, f'Shopee_{time.time_ns()}.log'), 
                            level=logging.INFO, format="%(asctime)s %(message)s")
            
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):

            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Init driver and capture object
            logging.info(f'Starting capture {url} to {file_path}')
            shopee = ShopeeLoader()
            capture = AsyncWebTrafficCapture()

            # Start capture
            capture.capture(interface, f'{file_path}.pcap')

            # Interact with shopee
            shopee.load(url)
            shopee.scroll_slowly_to_bottom(300, 1)

            # Turn off capture and driver
            capture.terminate()
            shopee.close_driver()

    except KeyboardInterrupt:
        shopee.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        shopee.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {file_path}')
        raise e