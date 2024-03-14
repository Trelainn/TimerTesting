import requests
import datetime
import camera
import time
import network_registration
import RPi.GPIO as GPIO
import serial
import wifi_management
import os
from threading import Thread

status = {'antenna_on': False, 'battery_percentage': 100, 'camera_on': False, 'date': 0, 'id': 0, 'internet_available':False, 'led_status': 'NONE', 'pcb_connection': False, 'race_number':0, 'race_status':'None', 'temperature': 0}
camera = camera.Camera()
camera.create_camera(image_width=1280, image_height=720, fps=20)
camera.stop_camera()
serialport = None
internet_available = False
antenna_on = False
led_status = 'Starting'
register_in_network = None
times = {}
lap_threshold = 20

def readSerial():
    while True:
        reading = serialport.readlines()
        if reading:
            try:
                data = {"Temperature": float(reading[1].decode().replace('\r', '').replace('\n','')), 
                        "Voltage_C1": float(reading[3].decode().replace('\r', '').replace('\n','')),
                        "Voltage_C2": float(reading[5].decode().replace('\r', '').replace('\n','')),
                        "Voltage_C3": float(reading[7].decode().replace('\r', '').replace('\n','')),
                        "Voltage_C4": float(reading[9].decode().replace('\r', '').replace('\n','')),
                        "Voltage_Charger": float(reading[11].decode().replace('\r', '').replace('\n','')),
                        "Button_Pressed": True if int(reading[13].decode().replace('\r', '').replace('\n','')) == 1 else False,
                        "Raspberry_Connected": True if int(reading[15].decode().replace('\r', '').replace('\n','')) == 1 else False,
                        "Starting_System": True if int(reading[17].decode().replace('\r', '').replace('\n','')) == 1 else False,
                        "System_Shut_Down": True if int(reading[19].decode().replace('\r', '').replace('\n','')) == 1 else False,
                        "Charging": True if int(reading[21].decode().replace('\r', '').replace('\n','')) == 1 else False,
                        "Fully_Charged": True if int(reading[23].decode().replace('\r', '').replace('\n','')) == 1 else False, 
                        "Camera_On": camera.get_camera_on(),
                        "Antenna_On": antenna_on,
                        "Internet_Available": internet_available, 
                        "LED_Status": led_status
                        }
                requests.post("http://localhost:8080/update_status", json=data)
                if data['System_Shut_Down'] == True:
                    print('OFF')
                    os.system('shutdown now')
                #print(response)
                #print(data)
            except:
                print(reading)

def registerInNetwork():
    network_registration.network_registration().register()

def checkStatus():
    global times
    while True:
        response = requests.get('http://localhost:8080/system_parameters')
        status['race_status'] = response.json()['race_status']
        if status['race_status'] == 'racing':
            if camera.get_camera_on() == False:
                camera.start_camera()
        else:
            if camera.get_camera_on() == True:
                camera.stop_camera()
                times = {}
        time.sleep(1)

def checkInternetConnection():
    global internet_available
    while True:
        try:
            response = requests.get("https://www.google.com")
            internet_available = True if (response.status_code == 200) else False
        except:
            pass
        #print(response.status_code)
        time.sleep(60)

def updateWifiList():
    global register_in_network
    while True:
        change_wifi_newtwork = requests.get('http://localhost:8080/update_wifi_network').json()
        if change_wifi_newtwork['change'] == True:
            ssid = change_wifi_newtwork['SSID']
            password = change_wifi_newtwork['Password']
            if change_wifi_newtwork['Hotspot'] == True:
                wifi_management.hotspot(ssid, password)
            else:
                wifi_management.connect(ssid, password)
            register_in_network.stop()
            register_in_network = Thread(target=registerInNetwork, args=()).start()
        requests.post("http://localhost:8080/update_list_wifi_networks", json=wifi_management.list_wifi_networks())
        time.sleep(15)

def readRFID():
    serialport = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.01)
    while True:
        if status['race_status'] == 'racing':
            reading = serialport.readlines()
            if reading:
                tag = reading[0].decode().split('\r')[0]
                if tag == 'CONNECTED':
                    status['antenna_on'] = True
                tag_read = tag[2:]
                time_now = datetime.datetime.now()
                try:
                    if tag in times:
                        last_time = times[tag]
                        time_recorded = (time_now - last_time).microseconds/1000000.0
                        if time_recorded > lap_threshold:
                            times[tag] = time_now
                            Thread(target=saveLapTime, args=(tag_read, time_recorded, camera.buffer)).start()
                    else:
                        times[tag] = time_now
                except Exception as e:
                    print(e)
        else:
            time.sleep(1)

def saveLapTime(tag, time_recorded, video):
    response=requests.post("http://localhost:8080/record_time/", json={'tag': str(tag), 'time': str(time_recorded)})
    if response.json()['ok']:
        if response.json()['video_permission']:
            camera.create_video(video, response.json()['video_name'])

if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12, True)
    serialport = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
    Thread(target=readSerial, args=()).start()
    register_in_network = Thread(target=registerInNetwork, args=()).start()
    Thread(target=checkStatus, args=()).start()
    Thread(target=checkInternetConnection, args=()).start()
    Thread(target=updateWifiList, args=()).start()
    Thread(target=readRFID, args=()).start()
'''

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
