import serial

serialport = serial.Serial("/dev/ttyACM0", 9600, timeout=0.01)

while True:
    print(serialport.readlines(None))
