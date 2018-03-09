from SubMotors import SubMotors
from time import time, sleep


# Create the object
_SubMotors = SubMotors()

# Allow for startup time
sleep(5)

tStartTime = time()
counter = 0
wait = 10

while(counter < 10):	
	# Set forward
	_SubMotors.SetLeftSpeed  (5, True)
	_SubMotors.SetRightSpeed (5, True)
	_SubMotors.SetServoAngle (100, True)
	
	sleep(wait)
	
	# Turn off
	_SubMotors.SetLeftSpeed  (0, True)
	_SubMotors.SetRightSpeed (0, True)
	_SubMotors.SetServoAngle (0, True)
	
	sleep(wait/5)
	
	# Set reverse
	_SubMotors.SetLeftSpeed  (5, False)
	_SubMotors.SetRightSpeed (5, False)
	_SubMotors.SetServoAngle (100, False)
	
	sleep(wait)
	
	# Turn off
	_SubMotors.SetLeftSpeed  (0, True)
	_SubMotors.SetRightSpeed (0, True)
	_SubMotors.SetServoAngle (0, True)
	
	sleep(wait/5)
	
	counter = counter + 1