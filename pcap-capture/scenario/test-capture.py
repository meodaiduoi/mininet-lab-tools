# config and environment
import tomli
import sys, os
import sslkeylog
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['test-capture']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# sslkeylog.set_keylog(os.environ.get('SSLKEYLOGFILE'))
# os.putenv('SSLKEYLOGFILE', './output/ssl-key.log',)


# Code start from here
from webcapture.pcapcapture import QUICTrafficCapture
from webcapture.ggservice import YoutubePlayer

if __name__ == '__main__':
    # Save ssl key to file
    os.environ['SSLKEYLOGFILE'] = './output/ssl-key.log'
    
    # Load youtube page
    youtube = YoutubePlayer('https://www.youtube.com/watch?v=9bZkp7q19f0')
    
    # Start capture
    capture = QUICTrafficCapture(interface, pcap_filename='./output/test.pcap',autostop='duration:15')
    youtube.play_button()
    youtube.fast_forward(10)
    print(capture.capture("aaa", "aaa"))
    capture.__apply_filter()
    youtube.close_driver()

