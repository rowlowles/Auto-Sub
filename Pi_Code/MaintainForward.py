# This keep the sub moving forward, corrects for changes in the X-Y direction
# Calling this alone will not correct for any depth variations
import time
import math

class MaintainForward:
	def __init__(self):
		# The basic speed to send to the motors
		self.baseSpeed = 50
		# The maximum amount the speed can change
		self.maxBump = 50
		# The maximum deflection we can expect
		self.maxDeflection = 15
		# This keeps track of the fact that we recored the state we want to maintain
		self.StateCaptured = False
		# This is an approximation to the forward speed, used in the the acceleration correction 
		self.Vx = 0.01		
		
	def CaptureState (self, angles, depth):
		self.yaw   = angles[2]
		self.TargetY = angles[3]
		self.TargetYaw = self.yaw
		self.StateCaptured = True
	
	def UpdateState (self, angles, depth):
		self.yaw   = angles[2]
		self.yPos  = angles[3]
		
		# Correct for drift in y
		# diffY = self.TargetY - self.yPos
		# diffInYaw = math.degrees(math.atan2(abs(diffY), self.Vx))
		# if(diffY > 0):
			# self.TargetYaw = self.TargetYaw + diffInYaw
		# else:
			# self.TargetYaw = self.TargetYaw - diffInYaw
		
		diffYaw = abs(self.yaw - self.TargetYaw)
		
		# Correct for yaw changes
		if( diffYaw > 270 ):
			diffYaw = 360 - diffYaw
			
		if( diffYaw > 1 ):
			# Take corrective actions
			speedBump = min( self.maxBump, self.maxBump * diffYaw  / self.maxDeflection )
			print( speedBump )
			if( self.yaw > self.TargetYaw):
				# We are turning clockwise, make the right motor stronger
				return[self.baseSpeed - speedBump, True, self.baseSpeed + speedBump, True, None, None]
				
			else:
				# We are turning counter clockwise, make the left motor stronger
				return[self.baseSpeed + speedBump, True, self.baseSpeed - speedBump, True, None, None]
		
		return[self.baseSpeed, True, self.baseSpeed, True, None, None]