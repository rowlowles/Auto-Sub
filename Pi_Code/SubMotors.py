# This class controls all the motors of the submarine
import Adafruit_PCA9685
from time import sleep

FREQ = 60 # Hz
PULSES_PER_SECOND = 1000000 / FREQ # Pulse per second
US_PER_PULSE = PULSES_PER_SECOND / 4096 # Micro seconds per pulse

b =   3.7037037037037037
a = -37.03703703703695

class SubMotors:
	
	def __init__(self):
		# Map the pins for each motor
		self._LeftMotorChannel  = 6
		self._RightMotorChannel = 5
		self._ServoMotorChannel = 3
		
		# Create the PWM object
		self._pwm = Adafruit_PCA9685.PCA9685()
		self._pwm.set_pwm_freq(FREQ)
		
		# Set the limits for each motor
		self._LeftForwardLimit    = 2000 # MicroSeconds
		self._LeftUpperStopValue  = 1545 # MicroSeconds
		self._LeftLowerStopValue  = 1455 # MicroSeconds
		self._LeftReverseLimit    = 1000 # MicroSeconds
		
		self._RightForwardLimit    = 2000 # MicroSeconds
		self._RightUpperStopValue  = 1545 # MicroSeconds
		self._RightLowerStopValue  = 1455 # MicroSeconds
		self._RightReverseLimit    = 1000 # MicroSeconds
		
		# Clockwise with increasing PWM
		self._ServoForwardLimit    = 1270 # MicroSeconds
		self._ServoUpperStopValue  = 1080 # MicroSeconds
		self._ServoLowerStopValue  = 1080 # MicroSeconds
		self._ServoReverseLimit    = 930  # MicroSeconds
		
		# Keep tabs on the state of each motor
		self._LeftCurrentSpeed  = (self._LeftUpperStopValue  + self._LeftLowerStopValue )/2 # MicroSeconds
		self._RightCurrentSpeed = (self._RightUpperStopValue + self._RightLowerStopValue)/2 # MicroSeconds
		self._ServoCurrentAngle = (self._ServoUpperStopValue + self._ServoLowerStopValue)/2 # MicroSeconds
		
		# Set all motors to stop
		self.WriteValueToChannel(self._LeftCurrentSpeed  , self._LeftMotorChannel )
		self.WriteValueToChannel(self._RightCurrentSpeed , self._RightMotorChannel)
		self.WriteValueToChannel(self._ServoCurrentAngle , self._ServoMotorChannel)
	
	def Calibrate(self, channel):
		wait = 3 
		
		print("Going to start")
		sleep(wait)
		
		# Writing top speed
		print("Writing high speed")
		self.WriteValueToChannel(2000, channel)
		sleep(wait) 
		
		# Writing top speed
		print("Writing high speed")
		self.WriteValueToChannel(1000, channel)
		sleep(wait) 
		
		# Writing top speed
		print("Writing high speed")
		self.WriteValueToChannel(1750, channel)
		sleep(wait) 
		
		# Writing top speed
		print("Writing high speed")
		self.WriteValueToChannel(1000, channel)
		sleep(wait) 
		
		# Writing top speed
		print("Writing high speed")
		self.WriteValueToChannel(1500, channel)
		sleep(wait) 
		
	def FixSpeed(self, speed):
		# Convert percentages to ratio
		speed = speed / float(100)
		
		# Make sure we don't overdo it
		if(speed > 1):
			speed = 1
		elif(speed < 0):
			speed = 0
			
		return(speed)
	
	def SetLeftSpeed (self, speed, forward):		
		
		# Translate speed into microseconds
		if(forward):
			self._LeftCurrentSpeed = self._LeftUpperStopValue + (self._LeftForwardLimit - self._LeftUpperStopValue) * self.FixSpeed(speed)
		else:
			self._LeftCurrentSpeed = self._LeftLowerStopValue - (self._LeftLowerStopValue - self._LeftReverseLimit ) * self.FixSpeed(speed)
		# Write microseconds to the left channel 
		self.WriteValueToChannel(self._LeftCurrentSpeed, self._LeftMotorChannel)
		
	def SetRightSpeed(self, speed, forward):
		# Translate speed into microseconds
		if(forward):
			self._RightCurrentSpeed = self._RightLowerStopValue - (self._RightLowerStopValue - self._RightReverseLimit) * self.FixSpeed(speed)
		else:
			self._RightCurrentSpeed = self._RightUpperStopValue + (self._RightForwardLimit - self._RightUpperStopValue) * self.FixSpeed(speed)
		
		# Write microseconds to the left channel 
		self.WriteValueToChannel(self._RightCurrentSpeed, self._RightMotorChannel)
	
	def SetServoAngle(self, speed, forward):
		# Translate speed into microseconds
		if(forward):
			self._ServoCurrentSpeed = self._ServoUpperStopValue + (self._ServoForwardLimit - self._ServoUpperStopValue) * self.FixSpeed(speed)
		else:
			self._ServoCurrentSpeed = self._ServoLowerStopValue - (self._ServoLowerStopValue - self._ServoReverseLimit) * self.FixSpeed(speed)
		# Write microseconds to the left channel 
		self.WriteValueToChannel(self._ServoCurrentSpeed, self._ServoMotorChannel)
		
	def WriteValueToChannel(self, value, channel):
		self._pwm.set_pwm(channel, 0, self.ToPulses(value))
	
	
	def ToPulses(self, MicroSeconds):
		
		return(int( (MicroSeconds - a) / float(b) ) )
