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
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        duration = config['youtubelive']['duration']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import YoutubeLivePlayer
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
        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'YoutubeLive_{time.time_ns()}.log'))
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(
            level=log_level,
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )

        while True:
            # Load url from playlist id
            ylive = YoutubeLivePlayer(profile_path=profile_path)
            for _ in range(3):
                filename = f'YoutubeLive_{time.time_ns()}'
                file_path = os.path.join(pcapstore_path, filename)
                # Save ssl key to file
                os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

                # Load youtube page
                ylive.load_in_playlist(-1)

                # Start capture
                capture = AsyncQUICTrafficCapture()
                capture.capture(interface, f'{file_path}.pcap')

                # Interact with youtube
                start_time = time.time()
                timer = 0
                skip_count = 0
                while ylive.player_state != 0 and timer <= duration:
                    if ylive.player_state != 1:
                        ylive.play()
                    if random.randint(1, 100) == 1: ylive.yliveplayer.fast_forward(1)
                    if ylive.player_state == -1:
                        skip_count += 1
                        if skip_count >= 5:
                            capture.terminate()
                            capture.clean_up()
                            capture = None
                            break
                    time.sleep(5)
                    timer = time.time() - start_time

                # Finish capture
                if capture:
                    capture.terminate()
                ylive.close()

    except KeyboardInterrupt:
        ylive.close()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: {file_path}')
        sys.exit(0)

    except Exception as e:
        ylive.close()
        capture.terminate()
        capture.clean_up()
        logging.critical(f'Error at: {file_path}')
        raise e

