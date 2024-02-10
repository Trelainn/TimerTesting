#!/usr/bin/python3

import cv2
import random
from datetime import datetime
from picamera2 import Picamera2
from threading import Thread

class Camera:
    '''
    buffer = []
    camera = None
    camera_working = False
    image_limit = 0
    '''
    def __init__(self, image_limit = 90, image_width = 640, image_height = 480):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (image_width, image_height)}))
        self.camera.start()
        self.camera_working = False
        self.buffer = []
        self.image_limit = image_limit
        #Thread(target=self.run_camera, args=()).start()

    def create_video(images, video_name):
        frame = images[0]
        height, width, layers = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        video = cv2.VideoWriter('videos/'+video_name, fourcc, 15, (width, height), True)

        for image in images:
            video.write(cv2.cvtColor(image,cv2.COLOR_BGRA2BGR))
        
        cv2.destroyAllWindows()
        video.release()

    def run_camera(self):
        while True:
            if self.camera_working:
                self.buffer.append(self.camera.capture_array())
                if len(self.buffer) > self.image_limit:
                    self.buffer.pop(0)
            cv2.waitKey(1)