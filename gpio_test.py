import RPi.GPIO as GPIO
import serial

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, True)
serialport = serial.Serial("/dev/ttyS0", 9600, timeout=0.01)

while True:
  reading = serialport.readlines()
  if reading:
    data = {"Temperature": float(reading[1].decode().replace('\r', '').replace('\n','')), 
            "Voltage_C1": float(reading[3].decode().replace('\r', '').replace('\n','')),
            "Voltage_C2": float(reading[5].decode().replace('\r', '').replace('\n','')),
            "Voltage_C3": float(reading[7].decode().replace('\r', '').replace('\n','')),
            "Voltage_C4": float(reading[9].decode().replace('\r', '').replace('\n','')),
            "Voltage_Charger": float(reading[11].decode().replace('\r', '').replace('\n','')),
            "Button_Pressed": True if int(reading[13].decode().replace('\r', '').replace('\n','')) == 1 else False,
            "Raspberry_Connected": reading[15].decode().replace('\r', '').replace('\n',''),
            "Starting_System": reading[17].decode().replace('\r', '').replace('\n',''),
            "System_Shut_Down": reading[19].decode().replace('\r', '').replace('\n',''),
            "Charging": reading[21].decode().replace('\r', '').replace('\n',''),
            "Fully_Charged": reading[23].decode().replace('\r', '').replace('\n','')  
            }
    print(data)