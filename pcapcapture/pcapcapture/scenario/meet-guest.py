import pyvirtualcam as pvc
import tomli
import sys, os
import sslkeylog
import pandas as pd
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        log_level = config['enviroment']['log_level']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# Code start from here
from webcapture.pcapcapture import AsyncQUICTrafficCapture
from webcapture.ggservice import GMeetGuest
import logging

if __name__ == '__main__':
    try:
        # Create timestamp

        # Save ssl key to file
        os.environ['SSLKEYLOGFILE'] = './output/Guest_sslkey_{timestamp}.log'

        # Load signin guest
        guest = GMeetGuest("")
        guest.user("account","passwrd")
        guest.signin()

        # Join meeting
        guest.code_meet("")
        guest.input_code()
        guest.join_meeting()

        # Start capture
        capture = AsyncQUICTrafficCapture()
        capture.capture(interface, './output/Guest_{timestamp}.pcap')


        # Turn off capture and driver
        capture.terminate()
        guest.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()