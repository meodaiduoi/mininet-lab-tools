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
        # start media before load url
        # virtual_media = FFMPEGVideoStream(logs_path=os.path.join(pcapstore_path, 'ffmpeg_logs'))
        virtual_media = FFMPEGVideoStream()
        virtual_media.play(
            random.choice(ls_subfolders(mkpath_abs(media_path)))
            )

        # Load invite url amd wait for join room
        gmeet = GMeetGuest(0, 0,
                           profile_path=profile_path)
        gmeet.load(meet_task.url)
        logging.info(f'Joining room {gmeet.meet_code}')
        
        # Check if camera and microphone is working
        if gmeet.cam_status != 1:
            raise Exception('Camera not found')
        if gmeet.mic_status != 1:
            raise Exception('Microphone not found')

        filename = f'GMeetGuest_{gmeet.meet_code}'
        file_path = os.path.join(pcapstore_path, filename)
        # Save ssl key to file
        os.environ['SSLKEYLOGFILE'] = os.path.join(sslkeylog_path, f'{filename}.log')

        # Wait for join room
        for attemp in range(10):
            time.sleep(5)
            if gmeet.joined:
                break
            if attemp >= 9:
                raise Exception('Join room timeout')

        capture = AsyncQUICTrafficCapture()
        capture.capture(interface, f'{file_path}.pcap')
        logging.info(f'Start capture meeting: {gmeet.meet_url} - Duration: {meet_task.durtation}, Saved at {file_path}')
        
        # Present in meeting
        time.sleep(meet_task.durtation)

        logging.info(f'End meeting at {gmeet.meet_url}, Saved at {file_path}')
        # Exit meeting
        capture.terminate()
        gmeet.close_driver()
        virtual_media.terminate()

    except Exception:
        capture.terminate()
        capture.clean_up()
        virtual_media.terminate()
        gmeet.close_driver()
        logging.error(f'Error at: {gmeet.meet_url} and {file_path}')


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
        # Create folder to store output
        pcapstore_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeet')
        sslkeylog_path = os.path.join(mkpath_abs(store_path), 'QUIC', 'GMeet', 'SSLKEYLOG')
        mkdir_by_path(pcapstore_path)
        mkdir_by_path(sslkeylog_path)

        file_handler = logging.FileHandler(filename=os.path.join(pcapstore_path, f'GMeetGuest_{time.time_ns()}.log'))
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

        # Create logger
        logging.basicConfig(
            level=log_level,
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logging.error('Keyboard Interrupt')
        sys.exit(0)


