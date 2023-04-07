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
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        url_list = config['facebook']['url_list']

        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.social import FacebookVideo
from webcapture.utils import *        

if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'FacebookVideo') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'FacebookVideo', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        logging.basicConfig(filename=os.path.join(pcapstore_path, f'FacebookVideo_{time.time_ns()}.log'), 
                            level=log_level, format="%(asctime)s %(message)s")

        # Load link from csv file
        df_link = pd.read_csv(url_list)

        for desc, url in zip(df_link['description'], df_link['url']):

            capture = AsyncQUICTrafficCapture()
            filename = f'{desc}'
            filepath = os.path.join(pcapstore_path, filename)
            
            if os.path.exists(f'{filepath}.pcap'):
                logging.warning(f'File {filepath}.pcap already exist, skipping...')
                continue
            
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load facebook
            logging.info(f'Starting capture {url} to {filepath}.pcap')
            facebook = FacebookVideo(disable_cache=True, 
                                     profile_path=profile_path
                                     fake_useragent=True)

            facebook.load(url)
            capture.capture(interface, f'{filepath}.pcap')

            while facebook.buffer_progress < 0.95:
                facebook.fast_forward()
                time.sleep(2)
                if facebook.video_progress > 0.95:
                    break
                
            # Turn off capture and driver
            capture.terminate()
            facebook.close_driver()

    except KeyboardInterrupt:
        facebook.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {filepath}')
        sys.exit(0)

    except Exception as e:
        facebook.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {filepath}')
        raise e