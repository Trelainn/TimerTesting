import requests
import datetime
import camera
import time
from threading import Thread

camera = camera.Camera(image_width=1280, image_height=720, fps=30)

time.sleep(5)

Thread(target=camera.create_video, args=(camera.buffer, 'Test1')).start()

camera.camera_working = True

time.sleep(2)

Thread(target=camera.create_video, args=(camera.buffer, 'Test2')).start()

time.sleep(3)

Thread(target=camera.create_video, args=(camera.buffer, 'Test3')).start()

print('Finished')

time.sleep(1)

camera.system_on = False
'''
def post_test(req):
    response = req.post("http://localhost/update_status", json={'temperature': 25})
    print(response)
    print(response.json())
    print(response.status_code)

session = requests.Session()
now = datetime.datetime.now()
print('Begin')
post_test(session)
print(datetime.datetime.now()-now)
now = datetime.datetime.now()
print('Begin')
post_test(session)
print(datetime.datetime.now()-now)
'''