# This class turns the sub 90 degrees
import time

class Turn90DegreeCW:
	def __init__(self, board, sub):
		self._MessageBoard = board
		self.TargetYaw = 0
		self.yaw = 0
		self._Sub = sub
	
	def Turn(self):
		self.yaw = self._Sub.GetAngles()[2]
		self.TargetYaw = self.yaw + 90
		self._MessageBoard.LogMessage("[Log] Turning to " + str(self.TargetYaw) + " (Turn90DegreeCW)\n")
		self.Loop()
	
	def Loop (self):
		self.yaw = self._Sub.GetAngles()[2]
		while(abs(self.TargetYaw - self.yaw) > 2):
			time.sleep(0.1) # Don't flood the device
			self.yaw = self._Sub.GetAngles()[2]
			speed = 15*abs(self.TargetYaw - self.yaw)/90.0 # Limit to 5%
			self._Sub.SendLeftSpeedPacket(speed, False)
			self._Sub.SendRightSpeedPacket(speed, True)
		self._MessageBoard.LogMessage("[Log] Done turning (Turn90DegreeCW)\n")