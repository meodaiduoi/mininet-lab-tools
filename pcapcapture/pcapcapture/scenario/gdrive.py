# config and environment
import tomli
import sys, os
import logging
import pandas as pd
import time
import re

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        url_list = config['gdrive']['url_list']
        temp_dir = config['gdrive']['temp_dir']
        timeout_dl = config['gdrive']['timeout_dl']
        
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
        
        temp_dir = mkdir_by_path(mkpath_abs(temp_dir))
        
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):
            
            # Load drive 
            logging.info(f'Loading {desc} from {url}')
            gdrive = GDriveDownloader(url, temp_dir,
                                      profile_path=profile_path)
            
            #First parameter is the replacement, second parameter is your input string
            gdrive_filename = re.sub('[^A-Za-z0-9]+', '_', gdrive.filename)
            filename = f'{gdrive_filename}_{gdrive.filesize[0]}{gdrive.filesize[1]}'
            filepath = os.path.join(pcapstore_path, filename)
            
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')
            
            # Check if file already exist
            if os.path.exists(f'{filepath}.pcap'):
                logging.warning(f'File {filepath}.pcap already exist, skipping...')
                gdrive.close_driver()
                continue
            
            # Start capture
            logging.info(f'Starting capture {url} to {filepath}.pcap')
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, f'{filepath}.pcap')

            # Download file
            gdrive.download()
            
            # TODO: make timeout scale with filesize
            timeout_countdown = timeout_dl
            while not gdrive.finished and timeout_countdown > 0:
                time.sleep(5)
                timeout_countdown -= 5
                logging.info(f'Download status is_finised: {gdrive.finished}, Timeout: {timeout_countdown} seconds left')
            logging.info(f'Download {gdrive.filename} {gdrive.filesize} finished')
                              
            # Terminate capture
            capture.terminate()
            
            # clean driver and close_driver
            gdrive.clean_download()
            gdrive.close_driver(quit=True)


    except KeyboardInterrupt:
        gdrive.clean_download()
        gdrive.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {filepath}')
        sys.exit(0)

    except Exception as e:
        gdrive.clean_download()
        gdrive.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {filepath}')
        raise e