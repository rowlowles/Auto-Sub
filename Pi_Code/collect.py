from Submarine import *

# Create the board
sub = Submarine(False)

sleep(10)

# Stop the motor
sub.UpdateMotorSpeed([0,True,0,True,sub._servoAngle])
print("Turning Off")
sleep(2)

sub.ShutDown()