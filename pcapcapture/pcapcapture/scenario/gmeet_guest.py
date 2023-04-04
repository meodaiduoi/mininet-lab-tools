# config and environment
import tomli
import sys, os
import logging
import sched, time

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
app = FastAPI()

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        log_level = config['enviroment']['log_level']
        media_path = config['enviroment']['media_path']
        profile_path = config['gmeet_guest']['profile_path']
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GMeetGuest
from webcapture.utils import *

@app.get("/")
def read_root():
    return {"Hello": "World"}

class MeetTask(BaseModel):
    url: str
    durtation: int | None = 600 # 10 minutes

@app.post('/join_room')
def join_room(meet_task: MeetTask):
    # Create folder to store output
    pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeetGuest') 
    sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeetGuest', 'SSLKEYLOG')
    mkdir_by_path(pcapstore_path)
    mkdir_by_path(sslkeylog_path)

    # Create logger
    file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'GMeetGuest_{time.time_ns()}.log'))
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    
    logging.basicConfig(
        level=log_level, 
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )

    filename = f'GMeetGuest_{time.time_ns()}'
    file_path = os.path.join(pcapstore_path, filename)
    # Save ssl key to file
    os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')
    
    gmeet = GMeetGuest(camera_id=0, mic_id=0)
    gmeet.load(meet_task.url)
    media_device = FFMPEGVideoStream(media_path, 30)
    
    capture = AsyncQUICTrafficCapture()
    capture.capture(interface, f'{file_path}.pcap')
    
    time.time(meet_task.durtation)

    capture.terminate()
    media_device.terminate()
    gmeet.close_driver()
    
if __name__ == '__main__':
    '''
    Folder structure:
    /{protocol: QUIC/HTTP}/{Service: GmeetGuest, Drive, etc}/{File: GmeetGuest_{timestamp}.pcap}:
                                                    .../SSLKEYLOG/GmeetGuest_{timestamp}.log
    '''
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logging.error('Keyboard Interrupt')
        sys.exit(0)


