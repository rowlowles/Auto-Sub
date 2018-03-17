from Submarine import *
import time
# Create the board
sub = Submarine(True)

sub.Forward(1)
count = 0
while count <= 100:
	sub.getControllerPackets()
	time.sleep(.1)
	count += 1

# Set the depth to 10
# sub.ChangeDepth(10)

# Turn ClockWise
# sub.ClockWiseTurn(60)

# Turn CounterClockWise
# sub.CounterClockWiseTurn(60)

#Set the motor to go back for 10 seconds
# sub.UpdateMotorSpeed([75,False,75,False,None])
# sleep(10)

# Stop the motor
sub.UpdateMotorSpeed([0,True,0,True,0,True,0,True])
print("Turning Off")
sleep(2)

sub.ShutDown()