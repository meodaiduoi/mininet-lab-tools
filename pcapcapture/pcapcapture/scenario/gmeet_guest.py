# config and environment
import tomli
import sys, os
import logging
import time, random

from fastapi import BackgroundTasks, FastAPI
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
        
        cam_id = config['gmeet_guest']['cam_id']
        mic_id = config['gmeet_guest']['mic_id']
        ffmpeg_cam_id = config['gmeet_guest']['ffmpeg_cam_id']
        ffmpeg_mic_name = config['gmeet_guest']['ffmpeg_mic_name']
                
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
    start_time_epoch: float | None = None

def task_meeting(meet_task: MeetTask):
    try:
    
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeetGuest') 
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeetGuest', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        # Create logger
        # !TODO: Change name to gmeet_host url
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
        
        gmeet = GMeetGuest(0, 0,
                           profile_path=profile_path)
        
        # start media before load url
        # virutal_media = FFMPEGVideoStream()
        # virutal_media.play(
        #     random.choice(ls_subfolders(media_path))
        #     )
        
        # Load invite url amd wait for join room
        gmeet.load(meet_task.url)
        for attemp in range(10):
            time.sleep(5)
            if gmeet.joined:
                break
            if attemp >= 9:
                raise Exception('Join room timeout')
        
        capture = AsyncQUICTrafficCapture()        
        capture.capture(interface, f'{file_path}.pcap')
        
        # TODO: Implenent start time with variant
        time.sleep(meet_task.durtation)

        capture.terminate()
        # virutal_media.terminate()
        gmeet.close_driver()
    
    except Exception:
        capture.terminate()
        capture.clean_up()
        # virutal_media.terminate()
        gmeet.close_driver()
        

@app.post('/join_room')
async def join_room(background_tasks: BackgroundTasks, meet_task: MeetTask):
    background_tasks.add_task(task_meeting, meet_task)
    return {'status': 'ok'}

    
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


