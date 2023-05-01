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
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeet')
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeet', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'GMeetHost_{time.time_ns()}.log'))
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]
        logging.basicConfig(
            level=log_level,
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )

        for meet_no in range(number_of_meeting):
            # Create meeting with virtual media
            virutal_media = FFMPEGVideoStream(logs_path=os.path.join(pcapstore_path, 'ffmpeg_logs'))
            virutal_media.play(
                random.choice(
                    ls_subfolders(mkpath_abs(media_path)))
                )
           
            gmeet = GMeetHost(cam_id, mic_id,
                              profile_path=profile_path)
            gmeet.create_meeting()
            logging.info(f'Created meeting: {gmeet.meet_url}')

            # Check if camera and microphone is working
            # if gmeet.cam_status != 1:
            #     raise Exception('Camera not found')
            if gmeet.mic_status != 1:
                raise Exception('Microphone not found')

            filename = f'GMeetHost_{gmeet.meet_code}'
            file_path = os.path.join(pcapstore_path, filename)
            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

            # Min-max duration must be at least greater than 60s window for guest to exit Recomended > 300s
            safe_exit_threshold = 60
            host_duration = random.randint(min_duration, max_duration)
            guest_duration = random.randint(round(host_duration*0.4), host_duration - safe_exit_threshold)
            for idx, guest_ip in enumerate(remote_ip):
                try:
                    # make sure these are at least 2 guests from start to the end of the meeting
                    if idx < 1:
                        rq.post(
                        f'http://{guest_ip}:{remote_port}/join_room',
                        # make sure to client close before server
                        json={'url': gmeet.meet_url, 'duration': (host_duration - safe_exit_threshold)})
                        continue

                    # rest of the guest can quit at anytime
                    else:
                        rq.post(
                            f'http://{guest_ip}:{remote_port}/join_room',
                            # make sure to client close before server
                            json={'url': gmeet.meet_url, 'duration': (guest_duration)})
                    logging.info(f'Guest {idx}, {guest_ip}:{remote_port} joined')
                
                except (rq.exceptions.HTTPError,
                        rq.exceptions.ConnectionError,
                        rq.exceptions.Timeout,
                        rq.exceptions.RequestException):
                    logging.error(f'Cannot connect to Guest: {idx}, {guest_ip}:{remote_port}')
                    continue

            # wait for webdrive from guest to connect
            logging.info('Waiting for guest to connect')
            time.sleep(20)

            logging.info('Waiting to accepting guest')
            for _ in range(25): # loop = 15: 1 guest, 25: 2 guest (First meeting)
                while gmeet.accept_guest():
                    pass
                time.sleep(1)

            # Initialize capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, f'{file_path}.pcap')
            logging.info(f'Capture started: Meetting {gmeet.meet_url} to {file_path}.pcap')
            time.sleep(host_duration)

            # Turn off capture and driver
            capture.terminate()
            logging.info(f'Capture ended: Meetting {gmeet.meet_url} to {file_path}.pcap')
            gmeet.close_driver()
            virutal_media.terminate()

    except KeyboardInterrupt:
        gmeet.close_driver()
        capture.terminate()
        capture.clean_up()
        virutal_media.terminate()
        logging.error(f'Error at: {gmeet.meet_url} and {file_path}')
        sys.exit(0)

    except Exception as e:
        gmeet.close_driver()
        capture.terminate()
        capture.clean_up()
        virutal_media.terminate()
        logging.critical(f'Error at: {gmeet.meet_url} and {file_path}')
        raise e