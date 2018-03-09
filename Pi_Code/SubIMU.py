import sys
import getopt

sys.path.append('.')
import numpy as np 
import RTIMU
import os.path
import time
import math
from functools import reduce
from multiprocessing import Process
from KalmanFilter import *
import statistics as s

SETTINGS_FILE = 'RTIMULib'

class SubIMU:
	def __init__(self, dataFile, connection, SaveSensorData):
		self._Ypos = 0
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
			self._IMU.setAccelEnable(True)
			self._IMU.setCompassEnable(False)
			self.magnetic_deviation = -13.7
			# Create and start the process
			p = Process(target=self.ReadIMU, args=(connection, dataFile, SaveSensorData))
			p.start()
			
	def AdjustHeading(self, yaw):
		if yaw < 90.1:
			heading = yaw + 270 - self.magnetic_deviation
		else:
			heading = yaw - 90 - self.magnetic_deviation
					
		if heading > 360.0:
			heading = heading - 360.0
				
		if heading < .1:
			heading = heading + 360.0
		
		return(heading)
					
	def ReadIMU(self, connection, dataFile, SaveSensorData):
		tLastRead = time.time()
		tStartTime = time.time()
		xAccelList = []
		yAccelList = []
		headingList = []
		startHeading = 0
		yAccelMaxNoise = 0
		yAccelBias = 0
		xAccelMaxNoise = 0
		xAccelBias = 0
		readIMU = True
		
		# Calibration Time
		while(tLastRead - tStartTime < 2):
			if self._IMU.IMURead():
				# Grab the data from the IMU
				data = self._IMU.getIMUData()
				fusionPose = data['fusionPose']
				Accel = data['accel']
				tLastRead = time.time()
				
				# Round the angles and acceleration 
				pitch = round(math.degrees(fusionPose[1]), 3)
				heading = self.AdjustHeading(round(math.degrees(fusionPose[2]), 3))
				XAccel = round(Accel[0], 3)
				YAccel = round(Accel[1], 3)
				
				# Update the array values
				xAccelList.append(XAccel)
				yAccelList.append(YAccel)	
				headingList.append(heading)
				
				# Update Y data
				if(abs(YAccel) > yAccelMaxNoise):
					yAccelMaxNoise = abs(YAccel)

				# Update X data
				if(abs(XAccel) > xAccelMaxNoise):
					xAccelMaxNoise = abs(XAccel)				
		
		# Calculate important parameters
		startHeading = s.mean(headingList)
		yAccelBias   = s.mean(yAccelList)
		xAccelBias   = s.mean(xAccelList)
		yAccelMaxNoise = 2 * s.stdev(yAccelList)
		xAccelMaxNoise = 2 * s.stdev(xAccelList)
		
		print("Calibration Done")
		
		while(readIMU):		
			if( (time.time() - tLastRead) > 5 ):
				# We lost connection log a message 
				connection.send("[Log] Lost connection (SubIMU)\n")
			
			if self._IMU.IMURead():
				# Grab the data from the IMU
				data = self._IMU.getIMUData()
				fusionPose = data['fusionPose']
				Accel = data['accel']
				delT = time.time() - tLastRead;
				# Update our watchdog time
				tLastRead = time.time()
				
				# Round the angles and acceleration 
				pitch = round(math.degrees(fusionPose[1]), 3)
				heading = self.AdjustHeading(round(math.degrees(fusionPose[2]), 3))
				XAccel = round(Accel[0], 3)
				YAccel = round(Accel[1], 3)
		

				# Remove the mean noise from the measurement
				YAccel = YAccel - yAccelBias
				if(abs(YAccel) < yAccelMaxNoise):
					YAccel = 0
				
				XAccel = XAccel - xAccelBias
				if(abs(XAccel) < xAccelMaxNoise):
					XAccel = 0
					
				# Find angle
				theta = np.radians(heading - startHeading)
				
				if(theta > 180):
					theta = 360 - theta
					
				c, sin = np.cos(theta), np.sin(theta)
				
				# Create rotation matrix
				R = np.matrix([[c, -sin], [sin, c]])
				
				# Find the local position
				xPosLocal = XAccel * 9.81 * delT * delT
				YPosLocal = YAccel * 9.81 * delT * delT
				
				[xPos, yPos] = R * np.matrix([[xPosLocal],[YPosLocal]]);
				
				yPos = float(yPos)
				self._Ypos = self._Ypos + yPos
				
				connection.send([0, pitch, heading, self._Ypos])
				
				if(SaveSensorData):
					dataFile.write( str(time.time()) + "," + str(pitch) + "," + str(heading) +"," + str(theta) + "," + str(YAccel) + "," + str(yPos) + "," + str(yAccelBias) + "," + str(yAccelMaxNoise) + "\n")
					dataFile.flush()
				
				if(connection.poll()):
					print("Here fuck")
					readIMU = False
					dataFile.close()