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
			
	# This method lets others post messages to the board to be sent out 
	def SendMessage(self, message):
		self.LogOutgoingMessage(message)
		self._sPort.write(bytearray(message,"ascii"))
		self._sPort.flush()
	
	# This method closes up things when it comes time to leave
	def CloseBoard(self):
		# Close our serial port
		self._sPort.close()
		# Close log file
		self._LogFile.close()
	
	# Sends a speed packet to the left motor
	def SendLeftSpeedPacket(self, speed, forward):
		if(forward):
			self.SendSpeedPacket("LM-",int(speed*100))
		else:
			self.SendSpeedPacket("LM+",int(speed*100))
	
	# Sends a speed packet to the right motor	
	def SendRightSpeedPacket(self, speed, forward):
		if(forward):
			self.SendSpeedPacket("RM+",speed = int(speed*100))
		else:
			self.SendSpeedPacket("RM-",speed = int(speed*100))
			
	def SendServoAnglePacket(self, angle):
		return # RETURN
		angle = int(angle)
		if( angle > 170 ):
			angle = 170 
			self.SendMessage("SM+" + str(angle) + "\n")
		elif( angle >= 100):
			self.SendMessage("SM+" + str(angle) + "\n")
		elif( angle >= 35):
			self.SendMessage("SM+0" + str(angle) + "\n")
		else:
			angle = 35
			self.SendMessage("SM+0" + str(angle) + "\n")
			
	# Formats the speed packet in order to send it
	def SendSpeedPacket(self, header, speed):
		if(speed >= 10000):
			speed = 9999
			self.SendMessage(header + "0" + str(speed) + "\n")
		elif(speed >= 1000):
			self.SendMessage(header + "0" + str(speed) + "\n")
		elif(speed >= 100):
			self.SendMessage(header + "00" + str(speed) + "\n")
		elif(speed >= 10):
			self.SendMessage(header + "000" + str(speed) + "\n")
		else:
			self.SendMessage(header + "0000" + str(speed) + "\n")