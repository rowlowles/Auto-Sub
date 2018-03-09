from Submarine import *

# Create the board
sub = Submarine(True)

sleep(30)

# Stop the motor
sub.UpdateMotorSpeed([0,True,0,True,sub._servoAngle])

# Turn the sub off
sub.ShutDown()

print("Turning Off")
sleep(2)

