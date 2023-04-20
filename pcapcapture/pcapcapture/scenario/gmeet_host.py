import tomli
import sys, os
import logging
import pandas as pd
import numpy as np
import time
import random
import requests as rq

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        profile_path = config['enviroment']['profile_path']
        log_level = config['enviroment']['log_level']
        media_path = config['enviroment']['media_path']
        
        cam_id = config['gmeet_host']['cam_id']
        mic_id = config['gmeet_host']['mic_id']
        ffmpeg_cam_id = config['gmeet_host']['ffmpeg_cam_id']
        ffmpeg_mic_name = config['gmeet_host']['ffmpeg_mic_name']
        remote_ip = config['gmeet_host']['remote_ip']
        remote_port = config['gmeet_host']['remote_port']
        number_of_meeting = config['gmeet_host']['number_of_meeting']
        min_duration = config['gmeet_host']['min_duration']
        max_duration = config['gmeet_host']['max_duration']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

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

        for meet_no in range(number_of_meeting):
            # Create logger
            logging.basicConfig(filename=os.path.join(pcapstore_path, f'GMeetHost_{time.time_ns()}.log'), 
                                level=log_level, format="%(asctime)s %(message)s")

        
            capture = AsyncQUICTrafficCapture()
            filename = f'GMeetHost_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Load meethost
            mhost = GMeetHost()
            virutal_media = FFMPEGVideoStream()
            meeting_duration = random.randint(min_duration, max_duration)
            
            media_files = ls_subfolders(media_path)
            virutal_media.start_video_stream(media_files[random.randint(0, len(media_files)-1)])
            for guest_ip in remote_ip:
                rq.post(
                    f'http://{guest_ip}:{remote_port}/start', 
                    json={'url': mhost.meet_url, 'duration': (meeting_duration-60)})

            for _ in range(60):                
                if mhost.accept_guest() == True:
                    mhost.accept_guest()
                else:
                    logging.error('no member join')
                time.sleep(1)
                
            capture.capture(interface, f'{file_path}.pcap')
            time.sleep(meeting_duration)
            
            # Turn off capture and driver
            capture.terminate()
            mhost.close_driver()

    except KeyboardInterrupt:
        mhost.close_driver()
        capture.terminate()
        capture.clean_up()
        logging.error(f'Keyboard Interrupt at: and {file_path}')
        sys.exit(0)

    except Exception as e:
        mhost.close_driver()
        capture.terminate()
        capture.clean_up()
        # logging.critical(f'Error at: {url} and {file_path}')
        raise e