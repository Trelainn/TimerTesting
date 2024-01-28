#!/usr/bin/python3

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import time

from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder

picam2 = Picamera2()

preview_config = picam2.create_preview_configuration(main={"size": (1980, 1080)})
picam2.configure(preview_config)

video_config = picam2.create_video_configuration(main={"size": (1980, 1080)})
picam2.configure(video_config)

encoder = H264Encoder(10000000)

picam2.start_recording(encoder, 'test.h264')
time.sleep(10)
picam2.stop_recording()

'''

picam2.start_preview(Preview.QTGL)

picam2.start()
time.sleep(2)

metadata = picam2.capture_file("test.jpg")
print(metadata)

picam2.close()
'''