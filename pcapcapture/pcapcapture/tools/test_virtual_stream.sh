ffmpeg -nostdin -re -i example.mp4 -f v4l2 /dev/video10 &
PULSE_SINK=virtual_speaker ffmpeg -i example.mp4 -f pulse "stream name"
kill $!