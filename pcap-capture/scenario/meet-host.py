import pyvirtualcam as pvc
import tomli
import sys, os
import sslkeylog
import pandas as pd
import numpy as np
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['meet-host']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

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

if __name__ == '__main__':
    try:
        # Create timestamp

        # Save ssl key to file
        os.environ['SSLKEYLOGFILE'] = './output/Host_sslkey_{timestamp}.log'

        # Load signin host
        host = GMeetHost("")
        host.user("account","passwrd")
        host.signin()
        
        # Join meeting
        host.code_meet("")
        host.input_code()
        host.join_meeting()

        # Start capture
        capture = AsyncQUICTrafficCapture()
        capture.capture(interface, './output/Host_{timestamp}.pcap')


        # Turn off capture and driver
        capture.terminate()
        host.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()