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
        url_list = config['gg-photos']['url_list']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GPhoto
from webcapture.utils import *        

if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Photo') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Photo', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'Photo_{time.time_ns()}.log'))
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(
            level=log_level, 
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url, quantity in zip(df_link['description'], df_link['url'], df_link['quantity']):
            for mode in ['normal', 'inspect']:
                
                filename = f'{desc}_{mode}'
                filepath = os.path.join(pcapstore_path, filename)
                # Save ssl key to file
                os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

                if os.path.exists(f'{filepath}.pcap'):
                    logging.info(f'File {filepath} already exists, skiping')
                    continue

                # Load photo
                logging.info(f'Starting capture {url} to {filepath}')
                photo = GPhoto(url, 
                               profile_path=profile_path,
                               disable_cache=True)
                photo.load(url)

                # Start capture
                capture = AsyncQUICTrafficCapture()
                capture.capture(interface, f'{filepath}.pcap')

                if mode == 'normal':
                    # Temporarily workaround for no pageheight issue
                    photo.scroll_slowly_to_bottom(70, 0.65)
                if mode == 'inspect':
                    time.sleep(10)
                    photo.inspect_image()
                    for _ in range(quantity):
                        photo.next_inspect_image()
                        time.sleep(1.4)
                
                capture.terminate()
                photo.close_driver()
            
    except KeyboardInterrupt:
        photo.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {filepath}')
        sys.exit(0)

    except Exception as e:
        photo.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {filepath}')
        raise e