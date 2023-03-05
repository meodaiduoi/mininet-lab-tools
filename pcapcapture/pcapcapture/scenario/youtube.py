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
        url_list = config['youtube']['url_list']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import YoutubePlayer
from webcapture.utils import *

if __name__ == '__main__':
    '''
    Folder structure:
    /{protocol: QUIC/WEB}/{Service: Youtube,Drive,etc}/{File: Youtube_{timestamp}.pcap}:
                                                   .../SSLKEYLOG/Youtube_{timestamp}.log
    '''
    # Create folder to store output
    pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Youtube')
    sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'Youtube', 'SSLKEYLOG')
    mkdir_by_path(pcapstore_path)
    mkdir_by_path(sslkeylog_path)

    # Create logger
    file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'Youtube_{time.time_ns()}.log'))
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )

    try:
        # Load link from csv file
        df_link = pd.read_csv(url_list)
        for desc, url in zip(df_link['description'], df_link['url']):

            # Create filename
            filename = f'{desc}_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Init driver and capture object
            logging.info(f'Starting capture {url} to {file_path}')
            youtube_player = YoutubePlayer(profile_path=profile_path)
            capture = AsyncQUICTrafficCapture()

            # Load youtube page and capture
            youtube_player.load(url)
            capture.capture(interface, f'{file_path}.pcap')

            # Interact with youtube
            youtube_player.play()
            while youtube_player.get_player_state() != 0:
                youtube_player.fast_forward(1)
                time.sleep(2)

            # Finish capture
            capture.terminate()
            youtube_player.close_driver()

    except KeyboardInterrupt:
        youtube_player.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        youtube_player.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {url} and {file_path}')
        raise e
