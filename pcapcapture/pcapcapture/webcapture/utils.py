import os
import subprocess, signal
import logging

# Directory utils
def ls_subfolders(rootdir):
    sub_folders_n_files = []
    for path, _, files in os.walk(rootdir):
        for name in files:
            sub_folders_n_files.append(os.path.join(path, name))
    return sorted(sub_folders_n_files)

def ls_file_in_current_folder(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def ls_folder_in_current_folder(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def mkpath_abs(path) -> str:
    # return os.path.abspath(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.expanduser(path))
    return path

def mkdir_by_path(path) -> str:
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f'Created directory: {path}')
        return path
    except NotADirectoryError:
        logging.error(f'Not a directory: {path} or already exists as a file')
        return ''
class FFMPEGVideoStream:
    def __init__(self, cam_id: int=10, mic_loopback_name: str='virtual_speaker'):
        self.cam_id = cam_id
        self.mic_loopback_name = mic_loopback_name
        self.video_process = None
        self.audio_process = None

    def play(self, video_path: str):
        if (self.video_process and self.audio_process) is None:
            self.video_process = subprocess.Popen(f'ffmpeg -nostdin -stream_loop -1  -re -i "{video_path}" -f v4l2 /dev/video{self.cam_id}',
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            logging.info(f'Starting ffmpeg process to stream video to /dev/video{self.cam_id}')

            self.audio_process = subprocess.Popen(f'PULSE_SINK="{self.mic_loopback_name}" ffmpeg -stream_loop -1  -i "{video_path}" -f pulse "stream name"',
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            logging.info(f'Starting ffmpeg process to stream audio to {self.mic_loopback_name}')

    # TODO: COULD Be improved
    def terminate(self) -> bool:
        if self.video_process and self.audio_process:
            # Stop ffmpeg
            result = subprocess.Popen(f'pgrep -P {self.video_process.pid}',
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
            video_parent_pid = int(result[0].decode('latin-1').split('\n')[0])
            os.kill(video_parent_pid, signal.SIGTERM)

            result = subprocess.Popen(f'pgrep -P {self.audio_process.pid}',
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
            print(result)
            audio_parent_pid = int(result[0].decode('latin-1').split('\n')[0])
            os.kill(audio_parent_pid, signal.SIGTERM)

            if self.video_process.returncode != 0:
                logging.error('Error: ffmpeg process terminated with non-zero return code')
                del self.video_process
                self.video_process = None
            if self.audio_process.returncode != 0:
                logging.error('Error: ffmpeg process terminated with non-zero return code')
                del self.audio_process
                self.audio_process = None
            else:
                logging.info('ffmpeg process terminated')
                return True
            return False

    def __del__(self) -> None:
        self.terminate()


