# This keep the sub moving forward
import time
import math

class MaintainForward:
	def __init__(self):
		self.baseSpeed = 50
		self.accelConverstion = 0
		self.maxBump = 50
		self.maxAngleChange = 15
		self.maxPitch = 15
		self.maxDeflection = 15
		self.StateCaptured = False
		self.Vx = 0.01
		
	def CaptureState (self, angles, depth):
		self.roll  = angles[0]
		self.pitch = angles[1]
		self.yaw   = angles[2]
		self.TargetY = angles[3]
		self.TargetYaw = self.yaw
		self.TargetPitch = self.pitch
		self.StateCaptured = True
	
	def UpdateState (self, angles, depth):			
		self.roll  = angles[0]
		self.pitch = angles[1]
		self.yaw   = angles[2]
		self.yPos  = angles[3]
		
		# Correct for drift in y
		# diffY = self.TargetY - self.yPos
		# diffInYaw = math.degrees(math.atan2(abs(diffY), self.Vx))
		# if(diffY > 0):
			# self.TargetPitch = self.TargetPitch + diffInYaw
		# else:
			# self.TargetPitch = self.TargetPitch - diffInYaw
		
		diffYaw = abs(self.yaw - self.TargetYaw)
		diffPitch = 0 # abs(self.pitch - self.TargetPitch)
		servoAngle = None
		servoDirection = True
		
		# Correct for pitch changes
		if( diffPitch > 1 ):
			angleBump = 100 * float(diffPitch)  / self.maxPitch
			servoAngle = angleBump
			if( self.pitch > self.TargetPitch ):
				# We are going down, turn us up 
				servoDirection = False
			else:
				# We are going up, turn us down 
				servoDirection = True
		
		# Correct for yaw changes
		if( diffYaw > 270 ):
			diffYaw = 360 - diffYaw
			
		if( diffYaw > 1 ):
			# Take corrective actions
			speedBump = min( self.maxBump, self.maxBump * diffYaw  / self.maxDeflection )
			print( speedBump )
			if( self.yaw > self.TargetYaw):
				# We are turning clockwise, make the right motor stronger
				return[self.baseSpeed - speedBump, True, self.baseSpeed + speedBump, True, servoAngle, servoDirection]
				
			else:
				# We are turning counter clockwise, make the left motor stronger
				return[self.baseSpeed + speedBump, True, self.baseSpeed - speedBump, True, servoAngle, servoDirection]
		
		return[self.baseSpeed, True, self.baseSpeed, True, 0, False]