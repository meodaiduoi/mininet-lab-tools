# config and environment
import tomli
import sys, os
import logging
import pandas as pd

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        url_list = config['lazada']['url_list']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)


# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import LazadaLoader
from webcapture.utils import *        

if __name__ == '__main__':
    try:
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):
            
            # Create folder to store output
            pcapstore_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Lazada') 
            sslkeylog_path = os.path.join(mkpath_abs(store_path), 'WEB', 'Lazada', 'SSLKEYLOG')
            mkdir_by_path(pcapstore_path)
            mkdir_by_path(sslkeylog_path)

            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load Lazada
            lazada = LazadaLoader()
            lazada.load(url)

            # Start capture
            capture = AsyncWebTrafficCapture()
            capture.capture(interface, f'{file_path}.pcap')

            # Interact with lazada
            lazada.load(url)
            lazada.scroll_slowly_to_bottom()

            # Turn off capture and driver
            capture.terminate()
            lazada.close_driver()

    except KeyboardInterrupt:
        lazada.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error('Keyboard Interrupt')
        sys.exit(0)

    except Exception as e:
        lazada.close_driver()
        capture.terminate()
        capture.clean_up()
        raise e