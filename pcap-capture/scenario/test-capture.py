# config and environment
import tomli
import sys, os
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['test-capture']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

os.putenv('SSLKEYLOGFILE', './output/ssl-key.log',)

# Code start from here
from webcapture.pcapcapture import QUICTrafficCapture
from webcapture.ggservice import YoutubePlayer

if __name__ == '__main__':
    youtube = YoutubePlayer('https://www.youtube.com/watch?v=9bZkp7q19f0')
    capture = QUICTrafficCapture(interface, pcap_filename='./output/test.pcap',autostop='duration:15')
    youtube.play_button()
    print(capture.capture())
    capture.apply_filter()
    youtube.close_driver()

