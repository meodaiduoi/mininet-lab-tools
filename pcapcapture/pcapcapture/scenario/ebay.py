# config and environment
import tomli
import sys, os
import logging
import pandas as pd
import time
import random

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        profile_path = config['enviroment']['nohttp3_profile_path']
        log_level = config['enviroment']['log_level']
        url_list = config['ebay']['url_list']
        min_page = config['ebay']['min_page']
        max_page = config['ebay']['max_page']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import EbayLoader
from webcapture.utils import *        

if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Ebay') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Ebay', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        logging.basicConfig(filename=os.path.join(pcapstore_path, f'Ebay_{time.time_ns()}.log'), 
                            level=log_level, format="%(asctime)s %(message)s")

        # Load link from csv file
        df_link = pd.read_csv(url_list)

        while True:
            capture = AsyncHTTPTrafficCapture()
            filename = f'Ebay_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load ebay
            ebay = EbayLoader(disable_cache=True, disable_http3=True)
            capture.capture(interface, f'{file_path}.pcap')

            for no_of_page in range(random.randint(min_page, max_page)):
                desc, url = df_link.iloc[random.randint(0, len(df_link)-1)].to_list()
                logging.info(f'Loading: {no_of_page}: {desc} - {url}')
                # Interact with ebay
                ebay.load(url)
                ebay.scroll_slowly_to_bottom(random.randint(400,650),
                                                random.randrange(1,2))

            # Turn off capture and driver
            capture.terminate()
            ebay.close_driver()

    except KeyboardInterrupt:
        ebay.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        ebay.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {file_path}')
        raise e