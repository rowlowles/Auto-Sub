# This class controls the camera that is attached to the sub
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

class SubIMU:
	def __init__(self, connection):
		# Create the camera object
		self._Camera = PiCamera()
		
		# Set camera parameters
		self._Camera.resolution(640, 480)
		self._Camera.framerate = 5 # Frames per second
		
		# Create storage
		rawCapture = PiRGBArray(camera, size=(640, 480))
		
		# Image Proccessing parameters
		self._dialationCycles = 2
		self._eroisionCycles = 2
		self._minRadius = 5
		
		self.greenLower  = (29, 86, 6)
		self.RedLower    = (29, 86, 6)
		self.YellowLower = (29, 86, 6)
		
		self.greenUpper  = (64, 255, 255)
		self.RedUpper    = (64, 255, 255)
		self.YellowUpper = (64, 255, 255)		
		
		# Allow the camera to warm up
		time.sleep(0.1)
		
		# Create and start the process
		p = Process(target=self.CaptureFrame, args=(connection, ))
		p.start()
					
	def CaptureFrame(self, connection, dataFile, SaveSensorData):
		# capture frames from the camera
		for frame in self._Camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			# Grab the raw NumPy array representing the image
			image = frame.array

			# Transfer the image into the HSV colour-space
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			
			# Preform a series of dilations and erosions to make sure we remove any false positives 
			mask = cv2.erode(hsv, None, iterations=self._dialationCycles)
			mask = cv2.dilate(mask, None, iterations=self._eroisionCycles)
			
			# We can now start to do fun processing, get all contours
			cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
			
			# Check if we found anything
			if( len(cnts) > 0):
				# We got some candidates, let's check them out
				# We want the golf ball that's closest to us, so let's get the biggest blob
				c = max(cnts, key=cv2.contourArea)
				# Let's tie a nice little circular bow around it
				(x, y), radius) = cv2.minEnclosingCircle(c)
				
				# Check if our bundle of joy is real
				if radius > self._minRadius:
					# Oh joy we have a chance, cut a square out
					radius = radius * 0.71 # Cos(45)
					mask = mask[ x-radius:x+radius, y-radius:y+radius]
					color = cv2.mean(mask)
					print(color)
					
			
			# Clear the stream in preparation for the next frame
			rawCapture.truncate(0)

			# Check if we have gotten the exit call
			if(connection.poll()):
				break				
					
			# Figure out what this will look like
			# connection.send([0, pitch, heading, yPos])