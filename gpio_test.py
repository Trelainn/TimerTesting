import RPi.GPIO as GPIO
import serial

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, True)
serialport = serial.Serial("/dev/ttyACM0", 9600, timeout=0.01)

while True:
  print(serialport.readlines())