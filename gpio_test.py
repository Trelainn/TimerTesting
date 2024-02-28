import RPi.GPIO as GPIO
import serial

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, True)
serialport = serial.Serial("/dev/ttyS0", 9600, timeout=0.01)

while True:
  reading = serialport.readlines()
  if reading:
    data = {"Temperature": reading[1].decode().replace('\r', '').replace('\n',''), 
            "Voltage_C1": reading[3].decode().replace('\r', '').replace('\n',''),
            "Voltage_C2": reading[5].decode().replace('\r', '').replace('\n',''),
            "Voltage_C3": reading[7].decode().replace('\r', '').replace('\n',''),
            "Voltage_C4": reading[9].decode().replace('\r', '').replace('\n',''),
            "Voltage_Charger": reading[11].decode().replace('\r', '').replace('\n',''),
            "Button_Pressed": reading[13].decode().replace('\r', '').replace('\n',''),
            "Raspberry_Connected": reading[15].decode().replace('\r', '').replace('\n',''),
            "Starting_System": reading[17].decode().replace('\r', '').replace('\n',''),
            "System_Shut_Down": reading[19].decode().replace('\r', '').replace('\n',''),
            "Charging": reading[21].decode().replace('\r', '').replace('\n',''),
            "Fully_Charged": reading[23].decode().replace('\r', '').replace('\n','')  
            }
    print(data)