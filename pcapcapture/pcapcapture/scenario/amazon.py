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
        url_list = config['amazon']['url_list']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)


# Code start from here
from webcapture.pcapcapture import *
from webcapture.ecomservice import AmazonLoader
from webcapture.utils import *        

if __name__ == '__main__':
    try:
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):
            
            # Create folder to store output
            pcapstore_path = os.path.join(mkpath_abs(store_path), 'HTTP', 'Amazon') 
            sslkeylog_path = os.path.join(mkpath_abs(store_path), 'HTTP', 'Amazon', 'SSLKEYLOG')
            mkdir_by_path(pcapstore_path)
            mkdir_by_path(sslkeylog_path)

            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load amazon
            amazon = AmazonLoader()
            amazon.load(url)

            # Start capture
            capture = AsyncWebTrafficCapture()
            capture.capture(interface, f'{file_path}.pcap')

            # Interact with amazon
            amazon.load(url)

            # Turn off capture and driver
            capture.terminate()
            amazon.close_driver()

    except KeyboardInterrupt:
        amazon.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error('Keyboard Interrupt')
        sys.exit(0)

    except Exception as e:
        amazon.close_driver()
        capture.terminate()
        capture.clean_up()
        raise e