from time import sleep,time
import datetime
import serial
import os

class MessageBoard:
	
	def __init__(self):
		# Create a file base name
		self._FileBase = os.getcwd() + "/Data/" + datetime.datetime.fromtimestamp(time()).strftime('%Y-%m-%d_%H_%M_%S')
		# Create a file to store logs
		self._LogFile = open(self._FileBase+"_logs.txt","w") 		
		# Create a file to store IMU data
		self._IMUFile = open(self._FileBase+"_imu.csv","w") 
		# Crate  a file to store Depth data
		self._DepthFile = open(self._FileBase+"_depth.csv","w")
		# Create a file to store joystick data
		self._JoystickFile = open(self._FileBase+"_joystick.csv","w")
		# Open the serial port to read serial data
		self._sPort = serial.Serial('/dev/ttyACM0',1000000, timeout=0.01) # 10 milliseconds
	
	# This method write a message to the log file
	def LogOutgoingMessage(self, message):
		self._LogFile.write("[Log] " + message.replace("\n","") + " (PI)\n")

	# This method write a message to the log file
	def LogMessage(self, message):
		self._LogFile.write(message)
			
	# This method closes up things when it comes time to leave
	def CloseBoard(self):
		self._LogFile.close()