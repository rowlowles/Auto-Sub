# This keep the sub moving forward
import time

class MaintainForward:
	def __init__(self):
		self.baseSpeed = 20
		self.maxBump = 20
		self.maxAngleChange = 5
		self.maxPitch = 30
		self.maxDeflection = 45
		self.StateCaptured = False
		
	def CaptureState (self, angles, depth, servoAngle):
		self.roll  = angles[0]
		self.pitch = angles[1]
		self.yaw   = angles[2]
		self.TargetYaw = self.yaw
		self.TargetPitch = self.pitch
		self.StateCaptured = True
		self.servoAngle = servoAngle
	
	def UpdateState (self, angles, depth, servoAngle):			
		self.roll  = angles[0]
		self.pitch = angles[1]
		self.yaw   = angles[2]
			
		diffYaw = abs(self.yaw - self.TargetYaw)
		diffPitch= abs(self.pitch - self.TargetPitch)
		
		# Correct for pitch changes
		if( diffPitch > 1 ):
			angleBump = self.maxAngleChange  * float(diffPitch)  / self.maxPitch
			if( self.pitch > self.TargetPitch ):
				# We are going down, turn us up 
				servoAngle = servoAngle - angleBump
			else:
				# We are going up, turn us down 
				servoAngle = servoAngle + angleBump
		
		
		# Correct for yaw changes
		if( diffYaw > 1):
			# Take corrective actions
			speedBump = self.maxBump * ( diffYaw )/self.maxDeflection
			if( self.yaw > self.TargetYaw ):
				# We are turning clockwise, make the right motor stronger
				return[self.baseSpeed, True, self.baseSpeed + speedBump, True, servoAngle]
				
			else:
				# We are turning counter clockwise, make the left motor stronger
				return[self.baseSpeed + speedBump, True, self.baseSpeed, True, servoAngle]
		
		return[self.baseSpeed, True, self.baseSpeed, True, servoAngle]