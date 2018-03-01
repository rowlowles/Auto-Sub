# This class turns the sub 90 degrees
import time

class MaintainForward:
	def __init__(self, board, sub):
		self._MessageBoard = board
		self._Sub = sub
		self.baseSpeed = 1
		self.maxBump = 20
		self.maxDeflection = 35
		self._Name = "(MaintainForward)\n"
		
	def Forward(self, length):
		angles = self._Sub.GetAngles()
		self.pitch = angles[1]
		self.yaw = angles[2]
		self.TargetYaw = self.yaw
		self.TargetPitch = self.yaw
		self._MessageBoard.LogMessage("[Log] Staying straight for" + str(length) + self._Name)
		self.Loop(length)
	
	def Loop (self, length):
		startTime = time.time()
		while(time.time() - startTime < length):
			time.sleep(0.1) # Don't flood the device
			
			angles = self._Sub.GetAngles()
			self.pitch = angles[1] 
			self.yaw = angles[2]
			
			diffYaw = abs(self.yaw - self.TargetYaw)
			
			# Correct for pitch changes
			
			# Correct for yaw changes
			if( diffYaw > 1):
				# Take corrective actions
				speedBump = self.maxBump * ( diffYaw )/self.maxDeflection
				if( self.yaw > self.TargetYaw ):
					# We are turning clockwise, make the right motor stronger
					self._Sub.SendRightSpeedPacket(self.baseSpeed + speedBump, True)
					self._Sub.SendLeftSpeedPacket(self.baseSpeed, True)
				else:
					# We are turning counter clockwise, make the left motor stronger
					self._Sub.SendLeftSpeedPacket(self.baseSpeed + speedBump, True)
					self._Sub.SendRightSpeedPacket(self.baseSpeed, True)
					
		self._MessageBoard.LogMessage("[Log] Time done, leaving " + self._Name)