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
        url_list = config['gg-drive']['url_list']
        timeout = config['gg-drive']['timeout']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GDriveDownloader  
from webcapture.utils import *         

if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Drive') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Drive', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'Drive_{time.time_ns()}.log'))
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
            
            # Check if file already exist
            if os.path.exists(f'{filepath}.pcap'):
                logging.warning(f'File {filepath}.pcap already exist, skipping...')
                continue
            
            # Load drive 
            logging.info(f'Starting capture {url} to {filepath}.pcap')
            drive = GDriveDownloader(profile_path=profile_path)
            drive.load(url)

            # Start capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, f'{filepath}.pcap')

            # Download file
            drive.download()
            
            # TODO: make timeout scale with filesize
            while True and not drive.finished and timeout > 0:
                time.sleep(5)
                timeout -= 5
                logging.info(f'Waiting for download to finish, Timeout: {timeout} seconds left')

            # Turn off capture and driver
            capture.terminate()
            drive.close_driver()

            # Remove file download
            drive.clean_download()

    except KeyboardInterrupt:
        drive.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {filepath}')
        sys.exit(0)

    except Exception as e:
        drive.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {filepath}')
        raise e