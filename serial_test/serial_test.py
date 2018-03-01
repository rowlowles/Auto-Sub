import serial
from time import sleep
import threading

ser = serial.Serial('/dev/ttyACM0',38400,timeout=1)

def readLine(ser):
	while(True):
		print(ser.readline())
		sleep(0.1)

thread = threading.Thread(target=readLine, args=(ser,))
thread.start()

while(True):
	ser.write(b'LM+00200\n')
	ser.write(b'RM-00200\n')
	sleep(0.5)
