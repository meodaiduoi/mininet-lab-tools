# config and environment
import tomli
import sys, os
import logging
import time, random
try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        log_level = config['enviroment']['log_level']
        duration = config['youtubelive']['duration']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import YoutubePlayer, YoutubeLivePlayer
from webcapture.utils import *

if __name__ == '__main__':
    '''
    Folder structure:
    /{protocol: QUIC/WEB}/{Service: Youtube,Drive,etc}/{File: Youtube_{timestamp}.pcap}:
                                                    .../SSLKEYLOG/Youtube_{timestamp}.log
    '''
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'YoutubeLive') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'YoutubeLive', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        logging.basicConfig(filename=os.path.join(pcapstore_path, f'YoutubeLive_{time.time_ns()}.log'), 
                            level=log_level, format="%(asctime)s %(message)s")

        # Load url from playlist id
        ylive = YoutubeLivePlayer()
        while True:
            filename = f'YoutubeLive_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')
            
            for url_id in range(len(ylive.url_list)):
                # Load youtube page
                ylive.load_in_playlist(url_id)

                # Start capture
                capture = AsyncQUICTrafficCapture()
                capture.capture(interface, f'{file_path}.pcap')
                
                # Interact with youtube
                start_time = time.time()
                timer = 0
                while ylive.yliveplayer != 0 and timer <= duration:
                    if ylive.get_player_state() != 1:
                        ylive.play()
                    if random.randint(1, 10) == 1: ylive.yliveplayer.fast_forward(1)
                    ylive.yliveplayer
                    time.sleep(1)
                    timer = time.time() - start_time

                # Finish capture
                capture.terminate()
                ylive.close()
    
    except KeyboardInterrupt:
        ylive.close()
        capture.terminate()
        capture.clean_up()
        logging.error('Keyboard Interrupt')
        sys.exit(0)

    except Exception as e:
        ylive.close()
        capture.terminate()
        capture.clean_up()
        raise e

