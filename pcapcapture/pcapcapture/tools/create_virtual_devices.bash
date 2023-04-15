#!/bin/bash

# run once to create the virtual webcam
# sudo modprobe -r snd-aloop
sudo modprobe v4l2loopback devices=1 video_nr=10 max_buffers=2 exclusive_caps=1 card_label="Virtual WebCam"
pactl load-module module-null-sink sink_name="virtual_speaker" sink_properties=device.description="virtual_speaker"
pactl load-module module-remap-source master="virtual_speaker.monitor" source_name="virtual_mic" source_properties=device.description="virtual_mic"

# PULSE_SINK=virtual_speaker ffmpeg -stream_loop -1 -re -i example.mp4 -f v4l2 -vcodec rawvideo -s 640x480 /dev/video10 -f pulse "stream name"
# ffmpeg -stream_loop -1 -re -i example.mp4 -f v4l2 -vcodec rawvideo -s 640x480  /dev/video10 -f alsa -ac 2 -i hw:1,1,0
