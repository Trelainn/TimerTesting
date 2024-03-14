import serial

class Serial_communication:
    
    def run(self):
        #serialport = serial.Serial("/dev/ttyACM0", 9600, timeout=0.01)
        serialport = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.01)
        while True:
            reading = serialport.readlines()
            if reading:
                tag = reading[0].decode().split('\n')[0]
                print(tag)



serialtest = Serial_communication()
serialtest.run()