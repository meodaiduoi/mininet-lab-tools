# config and environment
import tomli
import sys, os
import pandas as pd
import time
import logging
import random

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        url_list = config['tiktok']['url_list']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.social import TiktokLoader
from webcapture.utils import *
        
if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Tiktok')
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Tiktok', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)
        
        # Create logger
        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'Tiktok_{time.time_ns()}.log'))
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(
            level=log_level, 
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )

        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):

            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Init driver and capture object
            logging.info(f'Starting capture {url} to {file_path}')
            tiktok = TiktokLoader(profile_path=profile_path)
            capture = AsyncHTTPTrafficCapture()

            # Load tiktok page and start capture
            capture.capture(interface, f'{file_path}.pcap')
            tiktok.load(url)
            
            start_time = time.time()
            timer = 0
    
            tiktok.play()
            # Load about 20-30 vid change url
            while tiktok.player_state != 0 and timer == 30:
                tiktok.arrow_click('DOWN')
                time.sleep(1)
                timer = time.time() - start_time

            # Turn off capture and driver
            capture.terminate()
            tiktok.close_driver()

    except KeyboardInterrupt:
        tiktok.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        tiktok.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {file_path}')
        raise e