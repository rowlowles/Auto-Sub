# This method will compute the required angle of attack for the fins in order to dive to a certain depth 

class GoToDepth:
	def __init__(self):
		self.StateCaptured = False
		
	def CaptureState (self, depth, targetDepth):
		# Capture our current depth
		self.depth = depth
		# Capture our desired depth
		self.targetDepth = targetDepth
		# Capture the current difference
		self.depthRange = abs(targetDepth - depth)
		# Report that our state has been captured
		self.StateCaptured = True
	
	def UpdateState (self, depth):
		# Capture the new state
		self.depth = depth
		
		# Find out how much more we need to go before 
		diffDepth = abs(self.depth - self.targetDepth)
			
		# See if we are done moving
		if( diffDepth > 1 ):
			# Take corrective actions
			angleOfAttack = 100 * (diffDepth/self.depthRange)
			
			if( self.depth > self.targetDepth):
				# We are under the depth we want to go to, set our angle to up
				return[None, None, None, None, angleOfAttack, False]
				
			else:
				# We are turning counter clockwise, make the left motor stronger
				return[None, None, None, None, angleOfAttack, True]
		else:
			# We have reached the depth, leave now
			return(False)