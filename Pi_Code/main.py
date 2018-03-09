from Submarine import *

# Create the board
sub = Submarine(False)

# Move forward for 10 seconds
sub.Dive(5)
sleep(5)
sub.Rise(7)

# Turn ClockWise
# sub.ClockWiseTurn(60)

# Turn CounterClockWise
# sub.CounterClockWiseTurn(60)

#Set the motor to go back for 10 seconds
# sub.UpdateMotorSpeed([75,False,75,False,None])
# sleep(10)

# Stop the motor
sub.UpdateMotorSpeed([0,True,0,True,0,True])
print("Turning Off")
sleep(2)

sub.ShutDown()