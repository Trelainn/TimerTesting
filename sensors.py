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
                print(data)
                requests.post("http://localhost:8080/update_status", json=data)
                if data['System_Shut_Down']:
                    print('OFF')
                    os.system('shutdown now')
                    print('Bye')
                #print(response)
                #print(data)
            except:
                print(reading)
            serialport.write(str.encode(chr(65+2)))

def writeLED():
    serialport.write(str.encode(chr(65+2)))
    time.sleep(1)
    serialport.write(str.encode(chr(65+2)))
    
def registerInNetwork():
    network_registration.network_registration().register()

def checkStatus():
    global times
    global lap_threshold
    while True:
        response = requests.get('http://localhost:8080/system_parameters')
        status['race_status'] = response.json()['race_status']
        lap_threshold = int(response.json()['lap_threshold'])
        if status['race_status'] == 'racing':
            requests.get('http://localhost:8080/race')
            if (camera.get_camera_on() == False):
                camera.start_camera()
        else:
            if (camera.get_camera_on()):
                camera.stop_camera()
            times = {}
        #print(times)
        #print(lap_threshold)
        #print()
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
                        time_recorded = int((time_now - last_time).microseconds/1000 + (time_now - last_time).seconds * 1000)
                        if time_recorded > (lap_threshold * 1000):
                            times[tag] = time_now
                            Thread(target=saveLapTime, args=(tag_read, time_recorded, camera.buffer)).start()
                    else:
                        times[tag] = time_now
                except Exception as e:
                    print(e)
        else:
            time.sleep(1)

def saveLapTime(tag, time_recorded, video):
    response=requests.post("http://localhost:8080/record_time", json={'tag': str(tag), 'time': str(time_recorded)})
    print (response.json())
    if response.json()['ok']:
        if response.json()['video_permission']:
            camera.create_video(video, response.json()['video_name'])
            requests.post("http://localhost:8080/saved_video", json={'tag': str(response.json()['tag']), 'race_number': str(response.json()['race_number']), 'lap_number': str(response.json()['lap_number'])})

def closePastRaces():
    requests.post("http://localhost:8080/close_past_races")
    
def setGPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12, False)
    time.sleep(1)
    GPIO.output(12, True)

if __name__ == "__main__":
    Thread(target=setGPIO, args=()).start()
    serialport = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
    Thread(target=closePastRaces, args=()).start()
    Thread(target=readSerial, args=()).start()
    #Thread(target=writeLED, args=()).start()
    register_in_network = Thread(target=registerInNetwork, args=()).start()
    Thread(target=checkStatus, args=()).start()
    Thread(target=checkInternetConnection, args=()).start()
    Thread(target=updateWifiList, args=()).start()
    Thread(target=readRFID, args=()).start()