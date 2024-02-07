from picamera2 import Picamera2
from threading import Thread
import cv2
import keyboard

def create_video(images, video_name, fps = 15):
    frame = images[0]
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height), True)

    for image in images:
        video.write(cv2.cvtColor(image,cv2.COLOR_BGRA2BGR))
    
    cv2.destroyAllWindows()
    video.release()

def save_current_images(image_limit = 90):
    while True:
        if camera_working:
            buffer.append(camera.capture_array())
            if len(buffer) > image_limit:
                buffer.pop(0)
        cv2.waitKey(1)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))

buffer = []
camera_working = False

Thread(target=save_current_images, args=()).start()

while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        user = input()
        if user == 'q': 
            camera.start()
            camera_working = True
            print("Camera working")
        if user == 'w':  
            camera_working = False
            camera.stop()
            print("Camera stopped")
        if user == 'e':  
            Thread(target=create_video, args=(buffer, "test.mp4")).start()
            print("Video created")
        if user == 'r':
            break  
            camera_working = False
            print("Camera stopped")
    except:
        break  # if user pressed a key other than the given key the loop will break