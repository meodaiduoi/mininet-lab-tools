import pyvirtualcam as pvc
import tomli
import sys, os
import logging
import pandas as pd
import numpy as np
import time
import random

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

def main():
    with pvc.Camera(width=640, height=480, fps=20) as cam:
        print(f'Using virtual camera: {cam.device}')
        while True:
            frame = cam.frames_sent
            cam.send(np.zeros((480, 640, 4), np.uint8))
            print(f'Sent frame {frame}')

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GMeetHost
from webcapture.utils import *    

if __name__ == '__main__':
    try:
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeetHost') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeetHost', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        logging.basicConfig(filename=os.path.join(pcapstore_path, f'GMeetHost_{time.time_ns()}.log'), 
                            level=log_level, format="%(asctime)s %(message)s")

        while True:
            capture = AsyncQUICTrafficCapture()
            filename = f'GMeetHost_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load meethost
            meethost = GMeetHost()
            capture.capture(interface, f'{file_path}.pcap')

            meethost.create_meetting()

            if meethost.accept_guest() == True:
                meethost.accept_guest()
            else:
                logging.error('no member join')

            # Turn off capture and driver
            capture.terminate()
            meethost.close_driver()

    except KeyboardInterrupt:
        meethost.close_driver()
        capture.terminate()
        capture.clean_up()
        # logging.error(f'Keyboard Interrupt at: {url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        meethost.close_driver()
        capture.terminate()
        capture.clean_up()
        # logging.critical(f'Error at: {url} and {file_path}')
        raise e