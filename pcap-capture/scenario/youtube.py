from webcapture.pcapcapture import AsycnQUICTrafficCapture
from webcapture.ggservice import YoutubePlayer
import os, sys
import pandas as pd
import tomli
import logging
import time

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        sys.path.insert(0, '../' )
except FileNotFoundError:
    print('Config file not found')
    exit(1)

# def main():
#     df = pd.read_csv("/home/bkcs/CaptureData/mininet-lab-tools-main/pcap-capture/scenario/Links Youtube (25-35p) - Trang tính1.csv")
#     df_link = df['Links']
#     for i in range(len(df_link)):
#         youtube_capture = AsycnQUICTrafficCapture()
#         youtube_capture.capture("youtube", "youtube")
#         youtube_driver = YoutubePlayer(df_link[i])
#         youtube_driver.load(df_link[i])
#         youtube_driver.play_button()
        
#         time.sleep(30)
#         youtube_capture.terminate()
#         youtube_driver.close_driver()

if __name__ == '__main__':
    # capture.capture("","aaa")
    try:
        df = pd.read_csv("/home/bkcs/CaptureData/mininet-lab-tools-main/pcap-capture/scenario/Links Youtube (25-35p) - Trang tính1.csv")
        df_link = df['Links']
        for i in range(len(df_link)):
            youtube_capture = AsycnQUICTrafficCapture()
            youtube_capture.capture("ens160", "youtube")
            youtube_driver = YoutubePlayer(df_link[i])
            youtube_driver.load(df_link[i])
            youtube_driver.play_button()
            
            time.sleep(30)
            youtube_capture.terminate()
            youtube_driver.close_driver()

    except KeyboardInterrupt:
        
        logging.error('Keyboard Inter')
        youtube_driver.close_driver()
        sys.exit()