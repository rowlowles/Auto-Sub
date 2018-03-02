from Submarine import *

# import yappi
# yappi.start()

# Create the board
sub = Submarine(True)
sub.Start()

sub.UpdateMotorSpeed([0,True,0,True,sub._servoAngle])

sleep(2)

sub.ShutDown()

# yappi.get_func_stats().print_all()
# yappi.get_thread_stats().print_all()
