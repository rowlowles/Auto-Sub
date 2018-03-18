from Submarine import *
import time
# Create the board
sub = Submarine(True)

sub.Forward(1)
count = 0
while count <= 1000:
	# Read 10 seconds of controller inputs
	sub.getControllerPackets()
	time.sleep(.01)
	count += 1

sub.UpdateMotorSpeed([0,True,0,True,0,True,0,True])
print("Turning Off")
time.sleep(2)

sub.ShutDown()