from Pi_Code import Submarine

#Test script to see if the controller works. No

sub = Submarine.Submarine(False)

while True:

	if sub._state == "idle":
		sub.UpdateJoystick()

	if sub._state == "manual":
		sub.UpdateJoystick()
