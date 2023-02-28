# config and environment
import tomli
import sys, os
import logging
import pandas as pd
import time

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        url_list = config['gg-photos']['url_list']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GPhotosPageLoader
from webcapture.utils import *        

if __name__ == '__main__':
    # Create folder to store output
    pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Photo') 
    sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Photo', 'SSLKEYLOG')
    mkdir_by_path(pcapstore_path)
    mkdir_by_path(sslkeylog_path)
    try:
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):
            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load photo
            photo = GPhotosPageLoader()
            photo.load(url)

            # Start capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, f'{file_path}.pcap')

            # Interact with Gphoto
            photo.download()

            # Finish capture
            capture.terminate()
            photo.close_driver()

    except KeyboardInterrupt:
        photo.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error('Keyboard Interrupt')
        sys.exit(0)

    except Exception as e:
        photo.close_driver()
        capture.terminate()
        capture.clean_up()
        raise e