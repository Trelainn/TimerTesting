#!/usr/bin/python3

import cv2
import random
from picamera2 import Picamera2

def create_video(images, video_name):
    #frame = cv2.imread(images[0])
    frame = images[0]
    height, width, layers = frame.shape
    print(str(width) + ',' + str(height))
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video = cv2.VideoWriter(video_name, fourcc, 30, (width, height))

    for image in images:
        video.write(image)

    cv2.destroyAllWindows()
    video.release()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))
picam2.start()

i = 0
limit = random.randint(100, 101)
buffer = []
cont = True

while cont:
    buffer.append(picam2.capture_array())
    if len(buffer) > 90:
        buffer.pop(0)
    cv2.waitKey(1)
    i = i + 1
    if i == limit:
        cont = False
    cv2.waitKey(1)

create_video(buffer, 'test_video.mp4')