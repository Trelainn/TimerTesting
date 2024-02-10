import requests
import datetime
import camera
import time

camera = camera.Camera()

time.sleep(1000)

camera.create_video(camera.buffer, 'Test1')

time.sleep(2000)

camera.create_video(camera.buffer, 'Test2')

time.sleep(3000)

camera.create_video(camera.buffer, 'Test3')
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