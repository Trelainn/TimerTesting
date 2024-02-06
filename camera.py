#!/usr/bin/python3

import cv2
import random
from picamera2 import Picamera2

def create_video(images, video_name):
    frame = images[0]
    height, width, layers = frame.shape
    print(str(width) + ',' + str(height))
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    video = cv2.VideoWriter(video_name, fourcc, 30, (width, height), True)

    for image in images:
        video.write(cv2.cvtColor(image,cv2.COLOR_BGRA2BGR))
    
    cv2.destroyAllWindows()
    video.release()

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))
camera.start()

i = 0
limit = random.randint(100, 101)
buffer = []
cont = True

while cont:
    buffer.append(camera.capture_array())
    if len(buffer) > 90:
        buffer.pop(0)
    i = i + 1
    if i == limit:
        cont = False
    cv2.waitKey(1)

create_video(buffer, 'test_video.mp4')