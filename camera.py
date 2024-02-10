#!/usr/bin/python3

import cv2
import time
from datetime import datetime
from picamera2 import Picamera2
from threading import Thread
from datetime import datetime

class Camera:

    def __init__(self):
        pass

    def create_video(self, images, video_name):
        if images:
            now = datetime.now()
            frame = images[0]
            height, width, layers = frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            video = cv2.VideoWriter('videos/'+video_name+'.mp4', fourcc, self.fps, (width, height), True)

            for image in images:
                video.write(cv2.cvtColor(image,cv2.COLOR_BGRA2BGR))
            
            cv2.destroyAllWindows()
            video.release()
            print(datetime.now()-now)
        else:
            print('no buffer')

    def run_camera(self):
        while self.system_on:
            if self.camera_working:
                self.buffer.append(self.camera.capture_array())
                if len(self.buffer) > self.image_limit:
                    self.buffer.pop(0)
            cv2.waitKey(1)

    def stop_camera(self):
        self.camera_working = False
        self.camera.stop()

    def start_camera(self):
        self.buffer = []
        self.camera.start()
        self.camera_working = True

    def create_camera(self, image_limit = 90, image_width = 640, image_height = 480, fps = 30):
        self.system_on = False
        time.sleep(1)
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (image_width, image_height)}))
        self.system_on = True
        self.image_limit = image_limit
        self.fps = fps
        Thread(target=self.run_camera, args=()).start()