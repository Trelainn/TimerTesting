import requests
import datetime
import camera
import time
import network_registration
from threading import Thread

def registerInNetwork():
    registration = network_registration()

if __name__ == "__main__":
    Thread(target=registerInNetwork, args=()).start()
    

'''
camera = camera.Camera()
camera.create_camera(image_width=1280, image_height=720, fps=20)
camera.start_camera()

time.sleep(5)

Thread(target=camera.create_video, args=(camera.buffer, 'Test1')).start()

time.sleep(2)

Thread(target=camera.create_video, args=(camera.buffer, 'Test2')).start()

camera.stop_camera()
time.sleep(3)
camera.create_camera(image_width=1920, image_height=1280, fps=20)
#amera.create_camera()#image_width=640, image_height=480, fps=30)
camera.start_camera()
time.sleep(5)

Thread(target=camera.create_video, args=(camera.buffer, 'Test3')).start()
Thread(target=camera.create_video, args=(camera.buffer, 'Test4')).start()
Thread(target=camera.create_video, args=(camera.buffer, 'Test5')).start()

print('Finished')

time.sleep(1)

camera.system_on = False
'''

'''
def post_test(req):
    response = req.post("http://192.168.1.65:8080/update_status", json={'temperature': 25})
    print(response)
    print(response.json())
    print(response.status_code)

session = requests.Session()
now = datetime.datetime.now()
print('Begin')
post_test(session)
print(datetime.datetime.now()-now)

'''
