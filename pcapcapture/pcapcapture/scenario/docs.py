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
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        url_list = config['gg-docs']['url_list']
        string_list = config['gg-docs']['strings']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GDocsPageLoader
from webcapture.utils import *    
        
if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Docs') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Docs', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'Docs_{time.time_ns()}.log'))
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(
            level=log_level, 
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        df_link = pd.read_csv(url_list)
        
        while True:
            for desc, url in zip(df_link['description'], df_link['url']):

                filename = f'{desc}_{time.time_ns()}'
                file_path = os.path.join(pcapstore_path, filename)
                # Save ssl key to file
                os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

                # Load docs
                logging.info(f'Starting capture docs to {file_path}')
                docs = GDocsPageLoader(profile_path=profile_path)
                docs.load(url)

            # Start capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, f'{file_path}.pcap')


            docs.strings = string_list
            docs.editor()

            # Turn off capture and driver
            capture.terminate()
            docs.close_driver()

    except KeyboardInterrupt:
        docs.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {file_path}')
        sys.exit(0)

    except Exception as e:
        docs.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {file_path}')
        raise e