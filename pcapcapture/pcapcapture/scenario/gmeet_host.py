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
        profile_path = config['gmeet_host']['profile_path']
        
        
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
            # !TODO: Change name to gmeet_host url
            logging.basicConfig(filename=os.path.join(pcapstore_path, f'GMeetHost_{time.time_ns()}.log'), 
                                level=log_level, format="%(asctime)s %(message)s")
        
            # Create meeting with virtual media
            virutal_media = FFMPEGVideoStream()
            virutal_media.play(random.choice(ls_subfolders(media_path)))
            # Initialize capture
            capture = AsyncQUICTrafficCapture()

            mhost = GMeetHost(cam_id, mic_id,
                              profile_path=profile_path)
            mhost.create_meeting()

            filename = f'GMeetHost_{time.time_ns()}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')


            meeting_duration = random.randint(min_duration, max_duration)
            
            for guest_ip in remote_ip:
                try:
                    rq.post(
                        f'http://{guest_ip}:{remote_port}/join_room', 
                        json={'url': mhost.meet_url, 'duration': (meeting_duration-40)})
                except (rq.exceptions.HTTPError,
                        rq.exceptions.ConnectionError,
                        rq.exceptions.Timeout,
                        rq.exceptions.RequestException):
                    logging.error(f'Cannot connect to {guest_ip}')
                    continue
                
            # wait for webdrive from guest to connect
            time.sleep(20)
            
            for _ in range(10):                
                while mhost.accept_guest():
                    pass
                time.sleep(1)
                
            capture.capture(interface, f'{file_path}.pcap')
            time.sleep(meeting_duration)
            
            # Turn off capture and driver
            mhost.close_driver()
            capture.terminate()
            virutal_media.terminate()

    except KeyboardInterrupt:
        mhost.close_driver()
        capture.terminate()
        capture.clean_up()
        virutal_media.terminate()
        logging.error(f'Keyboard Interrupt at: and {file_path}')
        sys.exit(0)

    except Exception as e:
        mhost.close_driver()
        capture.terminate()
        capture.clean_up()
        # virutal_media.terminate()
        # logging.critical(f'Error at: {url} and {file_path}')
        raise e