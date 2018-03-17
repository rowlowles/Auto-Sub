# This keep the sub at a target depth, corrects for changes in the Z direction
class MaintainDepth:
	def __init__(self):
		# The maximum deflection we can expect
		self.maxDeflection = 15
		# This keeps track of the fact that we recored the state we want to maintain
		self.StateCaptured = False
		
	def CaptureState (self, angles, depth):
		# Capture our current depth
		self.TargetDepth = depth
		# Set the state to captured
		self.StateCaptured = True
	
	def UpdateState (self, angles, depth):
		# Find the difference in the depth 
		diffDepth = abs(depth - self.TargetDepth)
		# Prepare the return values
		servoAngle = None
		servoDirection = True
		
		# Correct for depth changes
		if( diffDepth > 1 ):
			servoAngle = 100 * float(diffDepth)  / self.maxDeflection
			if( depth > self.TargetDepth ):
				# We are going down, turn us up 
				servoDirection = False
			else:
				# We are going up, turn us down 
				servoDirection = True
		
		return[None, None, None, None, servoAngle, servoDirection]