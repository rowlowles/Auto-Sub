#This class is meant to control the motors and access sensor values
from SubIMU import *
from SubMotors import *
from SubDepthSensor import * 
from threading import Thread, Lock
from multiprocessing import Process,Pipe
from MessageBoard import MessageBoard
from MaintainForward import MaintainForward
from MaintainDepth import MaintainDepth
from GoToDepth import GoToDepth
from ClockWiseTurn import ClockWiseTurn
from CounterClockWiseTurn import CounterClockWiseTurn
from time import sleep,time
SmallChange = 1e-1

class Submarine:
	def __init__(self, SaveSensorData):
		# Create variables to hold the current position
		self._roll  = 0
		self._pitch = 0
		self._yaw   = 0
		self._YPos  = 0
		self._angleFirstRead = True
		# Create variables to hold depth
		self._depth = 0 
		# Create variables to control the message passing between processes 
		self.IMUParnetConn, self.IMUChildConn = Pipe()
		self.depthParnetConn, self.depthChildConn = Pipe()
		# Make the message board
		self._messageBoard = MessageBoard()
		# Create the object
		self._SubMotors = SubMotors()
		# Create the IMU object
		self.IMU = SubIMU(self._messageBoard._IMUFile, self.IMUChildConn, SaveSensorData)
		# Check if we were able to connect to the IMU
		if(self.IMU == None):
			# Don't bother updating the angles we don't have an IMU 
			self._upateAngles = False
		else:
			self._upateAngles = True
		# Create the depth sensor object
		self.depthSensor = SubDepthSensor(self._messageBoard._DepthFile, self.depthChildConn, SaveSensorData)
		# Check if we were able to connect to the depth sensor
		if(self.depthSensor == None):
			# Don't bother updating the depth we don't have a sensor 
			self._upateDepth = False
		else:
			self._upateDepth = True
		# Create the Maintain Forward object
		self._maintainForward = MaintainForward()
		# Create the Maintain Depth object
		self._maintainDepth  = MaintainDepth()
		# Create the dive object
		self._goToDepth = GoToDepth()
		# Create a clockwise turn object
		self._clockWiseTurn = ClockWiseTurn()
		# Create a counterclockwise turn object
		self._counterClockWiseTurn = CounterClockWiseTurn()
		# Create the timing variables
		self._rateDiff = 25
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
				self._YPos  = message[3]

		# This method checks the IMU connection and update values
	def UpdateDepth(self):
		# Check if the Depth Sensor has posted a message
		if(self.depthParnetConn.poll()):
			message = self.depthParnetConn.recv()
			if(str(message).find("[Log]") != -1):
				self._messageBoard.LogMessage(message)
			else:
				self._depth = message
	
	def UpdateMotorSpeed(self,Packet):
		if(Packet == None or len(Packet) < 5):
			return
		
		if(Packet[0] != None):
			# if( abs(self._SubMotors._leftSpeed - Packet[0]) > SmallChange):
			self._leftSpeed = Packet[0]
			self._SubMotors.SetLeftSpeed(Packet[0],Packet[1])
		
		if(Packet[2] != None):		
			# if( abs(self._SubMotors._rightSpeed - Packet[2]) > SmallChange):
			self._rightSpeed = Packet[2]
			self._SubMotors.SetRightSpeed(Packet[2],Packet[3])
				
		if(Packet[4] != None):				
			# if( abs(self._SubMotors._servoAngle - Packet[4]) > SmallChange):
			self._servoAngle = Packet[4]
			self._SubMotors.SetServoAngle(Packet[4], Packet[5])
			
	def UpdateSubState(self):
		if(self._upateAngles):
			self.UpdateAngles()
		if(self._upateDepth):
			self.UpdateDepth()
		
	# This will maintain a trajectory
	def Forward (self, length):
		self.UpdateSubState()
		counter = 0
		startTime = time()
		
		# Capture the state of the submarine
		self._maintainForward.CaptureState([self._roll,self._pitch,self._yaw,self._YPos], self._depth)
		self._maintainDepth.CaptureState  ([self._roll,self._pitch,self._yaw,self._YPos], self._depth)
		
		while( time() - startTime < length):
			# Update the submarine state
			self.UpdateSubState()
			# Update the counter
			counter = counter + 1
			# Send message if enough time has passed
			if( counter == self._rateDiff):
				# This will correct for an X-Y Variation 
				self.UpdateMotorSpeed(self._maintainForward.UpdateState([self._roll,self._pitch,self._yaw,self._YPos], self._depth))
				# This will correct for an Z Variation
				self.UpdateMotorSpeed(self._maintainDepth.UpdateState([self._roll,self._pitch,self._yaw,self._YPos], self._depth))
				# Reset the counter
				counter = 0
	
	def ChangeDepth(self, depth):
		self.UpdateSubState()
		counter = 0
		startTime = time()
		
		# Capture the state of the submarine
		self._maintainForward.CaptureState([self._roll,self._pitch,self._yaw,self._YPos], self._depth)
		self._goToDepth.CaptureState (self._depth, depth)
		
		# Set a flag to notify us when we reach our desired depth 
		reachedDepth = False
		
		while( not reachedDepth ):
			# Update the submarine state
			self.UpdateSubState()
			# Update the counter
			counter = counter + 1
			# Send message if enough time has passed
			if( counter == self._rateDiff):
				# This will correct for an X-Y Variation 
				self.UpdateMotorSpeed(self._maintainForward.UpdateState([self._roll,self._pitch,self._yaw,self._YPos], self._depth))
				# Set the angle of attack so we can dive
				response = self._goToDepth.UpdateState(self._depth)
				if(response != False):
					self.UpdateMotorSpeed(response)
				else:
					reachedDepth = True
				# Reset the counter
				counter = 0

	def ClockWiseTurn (self, angle):
		self.UpdateSubState()
		counter = 0
		StopAngle = self._yaw + angle
		
		while( abs(StopAngle - self._yaw) > 1):
			# Update the submarine state
			self.UpdateSubState()
			# Update the counter
			counter = counter + 1
			# Send message if enough time has passed
			if( counter == self._rateDiff):
				if(not self._clockWiseTurn.StateCaptured):
					self._clockWiseTurn.CaptureState([self._roll,self._pitch,self._yaw],angle)
				self.UpdateMotorSpeed(self._clockWiseTurn.UpdateState([self._roll,self._pitch,self._yaw]))
				counter = 0 
				
	def CounterClockWiseTurn(self, angle):
		self.UpdateSubState()
		counter = 0
		StopAngle = self._yaw - angle
		
		while( abs(StopAngle - self._yaw) > 1):
			# Update the submarine state
			self.UpdateSubState()
			# Update the counter
			counter = counter + 1
			# Send message if enough time has passed
			if( counter == self._rateDiff):
				if(not self._counterClockWiseTurn.StateCaptured):
					self._counterClockWiseTurn.CaptureState([self._roll,self._pitch,self._yaw], angle)
				self.UpdateMotorSpeed(self._counterClockWiseTurn.UpdateState([self._roll,self._pitch,self._yaw]))
				counter = 0 
		
	def ShutDown(self):
		# Tell the IMU process to exits
		print("Here fuck # 2")
		self.IMUParnetConn.send("Close")
		self.depthParnetConn.send("Close")
		self._messageBoard.CloseBoard()