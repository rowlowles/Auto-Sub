# We need to import the filter we are going to use
from KalmanFilter import *
import numpy
import ms5837
import time

class DepthSensor:
	currentDepth = 0; # Relative to the MSL
		
		self.sensor = ms5837.MS5837_30BA()		
		# A is the matrix we need to create that converts the last state to the new one, in our case it's just 1 because we get depth measurements directly
		A = numpy.matrix([1])
		# H is the matrix we need to create that converts sensors readings into state variables, since we get the readings directly from the sensor this is 1
		H = numpy.matrix([1])
		# B is the control matrix, since this is a 1D case and because we have no inputs that we can change we can set this to zero. 
		B = 0
		# Q is the process covariance, since we want accurate values we set this to a very low value
		Q = numpy.matrix([0.00001])
		# R is the measurement covariance, using a conservative estimate of 0.1 is fair
		R = numpy.matrix([0.1])
		# IC is the original prediction of the depth, setting this to normal room conditions makes sense
		IC = self.currentDepth 
		# P is the initial prediction of the covariance, setting it to 1 is reasonable
		P = numpy.matrix([1])
		
		# We must initialize the sensor before reading it
		self.sensor.init()
		
		# Create the filter
		self._filter = KalmanFilter(A,B,H,IC,P,Q,R)
		
	def UpdateValue(self):
		if (self.sensor.read()):
			self._filter.Step(numpy.matrix([0]),numpy.matrix([self.sensor.depth()]))
			self.currentDepth = self._filter.GetCurrentState()[0,0]
			return [self.sensor.depth(),self.currentDepth]