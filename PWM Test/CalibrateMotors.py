from SubMotors import SubMotors
from time import time, sleep


# Create the object
_SubMotors = SubMotors()

# Allow for startup time
sleep(2)

tStartTime = time()

_SubMotors.Calibrate(6)