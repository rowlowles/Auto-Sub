#This class is meant to control the motors and access sensor values
import types
from SubIMU import *
from SubDepthSensor import * 
from threading import Thread, Lock
from multiprocessing import Process,Pipe
from MessageBoard import MessageBoard
from MaintainForward import MaintainForward
from ClockWiseTurn import ClockWiseTurn
from CounterClockWiseTurn import CounterClockWiseTurn
from Controller_Operations import ControllerOps
from time import sleep,time
SmallChange = 1e-1

class Submarine:
	def __init__(self, SaveSensorData):
		# Create variables to hold the current position
		self._roll  = 0
		self._pitch = 0
		self._yaw   = 0
		self._YAccel = 0 
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
		self.controllerConn, self.controllerConn = Pipe()
		# Create a variable to hold the state: stopped, auto, or manual controls
		self._state = "stopped"
		# Make the message board
		self._messageBoard = MessageBoard()
		# Create the IMU object
		self.IMU = SubIMU(self._messageBoard._IMUFile, self.IMUChildConn, SaveSensorData)
		# Create the depth sensor object
		self.depthSensor = SubDepthSensor(self._messageBoard._DepthFile, self.depthChildConn, SaveSensorData)
		# Create the joystick object
		self.joystick = controllerOps(self._messageBoard._joystickFile, self.controllerConn, SaveSensorData)
		# Create the Maintain Forward object
		self._maintainForward = MaintainForward()
		# Create a clockwise turn object
		self._clockWiseTurn = ClockWiseTurn()
		# Create a counterclockwise turn object
		self._counterClockWiseTurn = CounterClockWiseTurn()
		# Create the timing variables
		self._rateDiff = 75
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
				self._YAccel = message[3]

		# This method checks the IMU connection and update values

	def UpdateDepth(self):
		# Check if the Depth Sensor has posted a message
		if(self.depthParnetConn.poll()):
			message = self.depthParnetConn.recv()
			if(str(message).find("[Log]") != -1):
				self._messageBoard.LogMessage(message)
			else:
				self._depth = message

	def UpdateJoystick(self):
		# Check to see if Joystick sent a message
		if(self.controllerConn.poll()):
			message = self.controllerConn.recv()
			if (message):
				if isinstance(message, tuple):
					# This means we have motor controls
					# Speed and bool:Is Forward
					self._messageBoard.SendLeftSpeedPacket(abs(message[0]), (message[0] <= 0))
					self._messageBoard.SendRightSpeedPacket(abs(message[1]), (message[1] <= 0))

				if isinstance(message, int):
					# Must be a servo command
					self._messageBoard.SendServoAnglePacket(message)

				if isinstance(message, str):
					# Three possibilities: 'auto', 'manual', and 'stop' which toggle between the various modes
					# 'auto' flag is autonomous operation of the sub
					# 'manual' is control via the joystick
					# 'stop' freezes all motion, no auto or manual action
					# TODO: Determine a way of implementing these states.
					self._state = message

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
				self._rightSpeed = Packet[2]
				self._messageBoard.SendRightSpeedPacket(Packet[2],Packet[3])
		
		if(Packet[4] != None):				
			if( abs(self._servoAngle - Packet[4]) > SmallChange):
				Packet[4] = int(Packet[4])
				
				if(Packet[4] > 170):
					Packet[4] = 170
				elif(Packet[4] < 35):
					Packet[4] = 35
				
			self._servoAngle = Packet[4]
			self._messageBoard.SendServoAnglePacket(Packet[4])
			
	def UpdateSubState(self):
		self.UpdateAngles()
		self.UpdateDepth()
		self.CheckSerial()
		self.UpdateJoystick()

	# This will maintain a trajectory
	def Forward (self, length):
		self.UpdateSubState()
		counter = 0
		startTime = time()
		
		while( time() - startTime < length):
			# Update the submarine state
			self.UpdateSubState()
			# Update the counter
			counter = counter + 1
			# Send message if enough time has passed
			if( counter == self._rateDiff):
				if(not self._maintainForward.StateCaptured):
					self._maintainForward.CaptureState([self._roll,self._pitch,self._yaw,self._YAccel], self._depth, self._servoAngle)
				self.UpdateMotorSpeed(self._maintainForward.UpdateState([self._roll,self._pitch,self._yaw,self._YAccel], self._depth, self._servoAngle))
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
		self.IMUParnetConn.send(False)
		self.controllerConn.send(False)
		self.depthParnetConn.send(False)
		self._messageBoard.CloseBoard()
