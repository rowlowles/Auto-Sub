# This keep the sub moving forward
import time

class ClockWiseTurn:
	def __init__(self):
		self.baseSpeed = 50
		self.maxBump = 25
		self.StateCaptured = False
		
	def CaptureState (self, angles, angle):
		self.yaw   = angles[2]
		self.angle = angle
		self.TargetYaw = self.yaw + angle
		self.StateCaptured = True
	
	def UpdateState (self, angles):			
		# Get inputs
		self.yaw = angles[2]
		diffYaw  = abs(self.yaw - self.TargetYaw)
		
		# Correct for yaw changes
		if( diffYaw > 270 ):
			diffYaw = 360 - diffYaw
		
		# Correct for pitch changes
		if( diffYaw > 1 ):
			speedBump = min(self.maxBump,self.maxBump * ( diffYaw ) / self.angle)
			return[self.baseSpeed + speedBump, True, self.baseSpeed, False, None]
		
		return[None, True, None, True, None]