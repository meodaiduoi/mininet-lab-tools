# config and environment
import tomli
import sys, os
import sslkeylog
import pandas as pd
from logging import info, debug, warning, error, critical

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['youtube']['interface']
        sys.path.insert(1, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# sslkeylog.set_keylog(os.environ.get('SSLKEYLOGFILE'))
# os.putenv('SSLKEYLOGFILE', './output/ssl-key.log',)

# Directory
directory = "Youtube file"

# Directory path
path_dir = "D:/Capture/"

# Path
path = os.path.join(path_dir, directory)

# Create the directory in path
os.mkdir(path)
print("Directory '% s' created" % directory)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import YoutubePlayer

if __name__ == '__main__':
    try:
        # Read file csv and get links
        df = pd.read_csv("")
        df_link = df['Links']
        
        for i in range(len(df_link)):
            # Create timestamp

            # Save ssl key to file
            os.environ['SSLKEYLOGFILE'] = './Youtube file/Youtube_sslkey_{timestamp}.log'

            # Load youtube page
            youtube = YoutubePlayer(df_link[i])
            youtube.load(df_link[i])

            # Start capture
            capture = AsyncQUICTrafficCapture()
            capture.capture(interface, './Youtube file/Youtube_{timestamp}.pcap')
            youtube.play_button()

            # Turn off
            for _ in range(10):
                youtube.fast_forward(2)
                time.sleep(1)
            capture.terminate()
            youtube.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        # youtube.close_driver()
        sys.exit()