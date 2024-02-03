import serial

serialport = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

while True:
    print(serialport.readlines(None))
