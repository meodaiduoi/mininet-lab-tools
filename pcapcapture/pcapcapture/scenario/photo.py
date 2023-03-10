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
from webcapture.ggservice import GPhotosPageLoader
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
        for desc, url in zip(df_link['description'], df_link['url']):
            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load photo
            logging.info(f'Starting capture {url} to {file_path}')
            photo = GPhotosPageLoader(profile_path=profile_path)
            photo.load(url)

            # Start capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, f'{file_path}.pcap')
            
            try:
                times = 0
                if desc == 'Image':
                    photo.arrow_click('RIGHT')
                    time.sleep(random.randint(2,3))
                    times = times + 1
                    if times == random.randint(50, 100):
                        capture.terminate()
                        photo.close_driver()
            except:
                logging.error(f'Error at: {url}')
                
            try:
                if desc == 'Album':
                    photo.scroll_slowly_to_bottom(random.randint(300,400), random.randrange(1,2))
                    capture.terminate()
                    photo.close_driver()
            except:
                logging.error(f'Error at: {url}')

            # Select any images (random)
            # Next about 200 images and finish capture
            # Load new album and scroll
    
            # Finish capture
            # capture.terminate()
            # photo.close_driver()

    except KeyboardInterrupt:
        photo.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        photo.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {file_path}')
        raise e