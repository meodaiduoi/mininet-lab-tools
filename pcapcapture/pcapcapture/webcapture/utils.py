import os, sys
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

def mkpath_abs(path):
    # return os.path.abspath(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.expanduser(path))
    return  path

def mkdir_by_path(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except NotADirectoryError:
        logging.error(f'Not a directory: {path} or already exists as a file')

# def init_virutal_microphone():
#     # Load v4l2loopback module
#     os.system('sudo modprobe snd-aloop')

# def rm_virutal_microphone():
#     # Unload v4l2loopback module
#     os.system('sudo modprobe -r snd-aloop')

# https://narok.io/creating-a-virtual-webcam-on-linux/
# def init_virtual_cam(device_id: int=10, card_label=f'Default Cam') -> bool:
#     if os.path.exists(f'/dev/video{device_id}'):
#         os.system(f'sudo modprobe v4l2loopback \
#                    video_nr={device_id} max_buffers=2 \
#                    exclusive_caps=1 card_label="{card_label}"')
#     return True

# def rm_all_virtual_cam() -> bool:
#     os.system('sudo modprobe -r v4l2loopback')
#     return True

# def init_virtual_mic() -> bool:
#     os.system('pactl load-module module-null-sink sink_name="virtual_speaker" sink_properties=device.description="virtual_speaker"')
#     os.system('pactl load-module module-remap-source master="virtual_speaker.monitor" source_name="virtual_mic" source_properties=device.description="virtual_mic"')
#     return True

# def rm_virtual_mic() -> bool:
#     os.system('')
#     return True



class FFMPEGVideoStream:
    def __init__(self, device_id: int=10):
        self.device_id = device_id
        
        self.process = None

    # def start_(self, video_path: str):
    #     # Start ffmpeg
    #     if not self.process:
    #         logging.info(f'Starting ffmpeg process to stream video {video_path} to /dev/video{self.device_id}')
    #         self.process = subprocess.Popen(f'ffmpeg -stream_loop -1 -re -i {video_path}.mp4 \
    #                                         -f v4l2 -vcodec rawvideo -s 1280x720  /dev/video{self.device_id} \
    #                                         -f alsa -ac 2 -i hw:Loopback,1,0')

    def start_video_stream(self):
        video_process = subprocess.Popen('ffmpeg -nostdin -re -i myfile.mkv -f v4l2 /dev/video0',
                                        shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        audio_process = subprocess.Popen('PULSE_SINK=virtual_speaker ffmpeg -i myfile.mkv -f pulse "stream name"',
                                        shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        video_process_pid = video_process.pid
        audio_process_pid = audio_process.pid

    def terminate(self):
        if self.process:
            # Stop ffmpeg
            result = subprocess.Popen(f'pgrep -P {self.process.pid}',
                                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            parent_pid = int(result[0].decode('latin-1').split('\n')[0])
            os.kill(parent_pid, signal.SIGTERM)
            return_code = self.process.wait()
            if return_code != 0:
                logging.error('Error: ffmpeg process terminated with non-zero return code')
            logging.info('ffmpeg process terminated')
            return return_code

