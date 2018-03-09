from Pi_Code import Submarine
import time
#Test script to see if the controller works. No

time.sleep(10)

sub = Submarine.Submarine(False)

while True:

	if sub._state == "idle":
		sub.UpdateJoystick()
	if sub._state == "auto":
		sub.Forward(15)
	if sub._state == "manual":
		sub.UpdateJoystick()
