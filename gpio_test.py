import RPi.GPIO as GPIO
import serial

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, True)
serialport = serial.Serial("/dev/ttyS0", 9600, timeout=0.01)

while True:
  reading = serialport.readlines()
  if reading:
    for read in reading:
        print(read.decode())