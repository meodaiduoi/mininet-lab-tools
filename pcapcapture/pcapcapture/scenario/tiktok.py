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
        min_page = config['tiktok']['min_page']
        max_page = config['tiktok']['max_page']
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
            filepath = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Init driver and capture object
            logging.info(f'Starting capture {url} to {filepath}.pcap')
            tiktok = TiktokLoader(url, profile_path=profile_path, fake_useragent=True)
             
            # Check if captcha block
            while True:
                if tiktok.captcha_block:
                    input('Please solve captcha and press enter to continue')    
                else:
                    break

            # Load tiktok page and start capture
            capture = AsyncHTTPTrafficCapture()
            tiktok.next_video()
            capture.capture(interface, f'{filepath}.pcap')
    
            # Load about 100-200 vid change url
            for i in range(random.randint(min_page, max_page)):
                tiktok.next_video()
                # exit if captcha block
                if tiktok.captcha_block:
                    logging.error(f'Captcha block at: {url} and {filepath}')
                    # break
                time.sleep(random.randint(20, 60))
                
            # Turn off capture and driver
            capture.terminate()
            tiktok.close_driver()

    except KeyboardInterrupt:
        tiktok.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {filepath}')
        sys.exit(0)

    except Exception as e:
        tiktok.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {filepath}')
        raise e