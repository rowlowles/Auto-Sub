#This class is meant to control the motors and access sensor values
from SubIMU import *
from SubDepthSensor import * 
from threading import Thread, Lock
from multiprocessing import Process,Pipe
from MessageBoard import MessageBoard
from MaintainForward import MaintainForward
from time import sleep,time
SmallChange = 1e-1

class Submarine:
	def __init__(self, SaveSensorData):
		# Create variables to hold the current position
		self._roll  = 0
		self._pitch = 0
		self._yaw   = 0
		self._angleFirstRead = True
		# Create variables to hold depth
		self._depth = 0 
		# Create variables to hold the current speeds
		self._leftSpeed  = 0
		self._rightSpeed = 0
		self._servoAngle = 102
		# Create variables to control the message passing between processes 
		self.IMUParnetConn, self.IMUChildConn = Pipe()
		self.depthParnetConn, self.depthChildConn = Pipe()
		# Make the message board
		self._messageBoard = MessageBoard()
		# Create the IMU object
		self.IMU = SubIMU(self._messageBoard._IMUFile, self.IMUChildConn, SaveSensorData)
		# Create the depth sensor object
		self.depthSensor = SubDepthSensor(self._messageBoard._DepthFile, self.depthChildConn, SaveSensorData)
		# Create the Maintain Forward object
		self._maintainForward = MaintainForward()
		# Create the timing variables
		self._stateUpdateRate = float(1000) # Hz
		self._speedUpdateRate = float(5) # Hz
		self._rateDiff = int(self._stateUpdateRate/self._speedUpdateRate)
		# Create a method to leave
		self._exit = False
		
	# This method checks the IMU connection and update values
	def UpdateAngles(self):
		# Check if the IMU has posted a message
		if(self.IMUParnetConn.poll() or self._angleFirstRead):
			message = self.IMUParnetConn.recv()
			self._angleFirstRead = False
			if(str(message).find("[Log]") != -1):
				self._messageBoard.LogMessage(message)
			else:
				self._roll  = message[0]
				self._pitch = message[1]
				self._yaw   = message[2]	

		# This method checks the IMU connection and update values
	def UpdateDepth(self):
		# Check if the Depth Sensor has posted a message
		if(self.depthParnetConn.poll()):
			message = self.depthParnetConn.recv()
			if(str(message).find("[Log]") != -1):
				self._messageBoard.LogMessage(message)
			else:
				self._depth = message
	
	def CheckSerial(self):
		if(self._messageBoard._sPort.inWaiting()):
			message = self._messageBoard._sPort.readline()
			if( message != ''):
				try:
					message = message.decode('ascii')
					if(message.find("[Log]") != -1):
						self._messageBoard.LogMessage(message)
				except:
					message = ''
	
	def UpdateMotorSpeed(self,Packet):
		if(Packet == None or len(Packet) < 5):
			return
		
		if(Packet[0] != None):
			if( abs(self._leftSpeed - Packet[0]) > SmallChange):
				self._leftSpeed = Packet[0]
				self._messageBoard.SendLeftSpeedPacket(Packet[0],Packet[1])
		
		if(Packet[2] != None):		
			if( abs(self._rightSpeed - Packet[2]) > SmallChange):
				self._leftSpeed = Packet[2]
				self._messageBoard.SendRightSpeedPacket(Packet[2],Packet[3])
			
		if( abs(self._servoAngle - Packet[4]) > SmallChange):
			Packet[4] = int(Packet[4])
			
			if(Packet[4] > 170):
				Packet[4] = 170
			elif(Packet[4] < 35):
				Packet[4] = 35
				
			self._servoAngle = Packet[4]
			self._messageBoard.SendServoAnglePacket(Packet[4])
			
	
	# This is the main method of the submarine object, collects data from sensor while watching serial port and determining motion
	def Start (self):
		counter = 0
		startTime = time()
		while( not self._exit):
			if(time() - startTime > 20):
				self._exit = True
				
			self.UpdateAngles()
			self.UpdateDepth()
			self.CheckSerial()
			
			counter = counter + 1
			
			if( counter == self._rateDiff):
				if(not self._maintainForward.StateCaptured):
					self._maintainForward.CaptureState([self._roll,self._pitch,self._yaw], self._depth, self._servoAngle)
				
				self.UpdateMotorSpeed(self._maintainForward.UpdateState([self._roll,self._pitch,self._yaw], self._depth, self._servoAngle))
				counter = 0 
				
			# sleep(1/self._stateUpdateRate)
		
	def ShutDown(self):
		# Tell the IMU process to exits
		self.IMUParnetConn.send(False)
		self.depthParnetConn.send(False)
		self._messageBoard.CloseBoard()