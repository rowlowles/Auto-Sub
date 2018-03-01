import sys
import getopt

sys.path.append('.')
import numpy
import RTIMU
import os.path
import time
import math
from functools import reduce
from multiprocessing import Process
from KalmanFilter import *

SETTINGS_FILE = 'RTIMULib'

class SubIMU:
	def __init__(self, dataFile, connection, SaveSensorData):
		# Set the settings file for the IMU
		self.IMUSettings = RTIMU.Settings(SETTINGS_FILE)
		# Create the IMU object
		self._IMU = RTIMU.RTIMU(self.IMUSettings)
		if not self._IMU.IMUInit():
			# We were unable to turn on, we should not start the process
			return None
		else:
			self._Ready = False
			self._valuesRead = 0
			# Decide what sampling rate we want (HZ)
			self.SamplingRate = float(150)
			# Set the fusion parameter
			self._IMU.setSlerpPower(0.02)
			# Turn on the devices we want to use to locate
			self._IMU.setGyroEnable(True)
			self._IMU.setAccelEnable(False)
			self._IMU.setCompassEnable(False)
			self.magnetic_deviation = -13.7
			# Create and start the process
			p = Process(target=self.ReadIMU, args=(connection, dataFile, SaveSensorData))
			p.start()
			
	def ReadIMU(self, connection, dataFile, SaveSensorData):
		# Keep track of how many values have been read, this is to allow the kalman filter to converge before we start announcing values
		valuesRead = 0
		tLastRead = time.time()
		readIMU = True
		
		while(readIMU):
			# time.sleep(1/self.SamplingRate)
		
			if( (time.time() - tLastRead) > 5 ):
				# We lost connection log a message 
				connection.send("[Log] Lost connection (SubIMU)\n")
			
			if self._IMU.IMURead():
				if(not self._Ready):
					self._valuesRead +=1
					if(self._valuesRead == self.SamplingRate):
						self._Ready = True
						
				tLastRead = time.time()
				data = self._IMU.getIMUData()
				fusionPose = data['fusionPose']
				Gyro = data['gyro']

				pitch = round(math.degrees(fusionPose[1]), 3)
				yaw = round(math.degrees(fusionPose[2]), 3)
				
				if yaw < 90.1:
					heading = yaw + 270 - self.magnetic_deviation
				else:
					heading = yaw - 90 - self.magnetic_deviation
				if heading > 360.0:
					heading = heading - 360.0
				
				if heading < .1:
					heading = heading + 360.0
				
				if(self._Ready):
					connection.send([0,pitch,heading])
				
				if(SaveSensorData):
					dataFile.write( str(time.time()) + "," + str(pitch) + "," + str(heading) + "\n")
			
			if(connection.poll()):
				readIMU = connection.recv()
				dataFile.close()