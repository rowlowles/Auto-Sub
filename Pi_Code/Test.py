from Pi_Code import Controller_Operations, Submarine
from multiprocessing import Pipe, process
import time

time.sleep(5)

sub = Submarine.Submarine(False)

while True:

	if sub._state == "idle":
		sub.UpdateJoystick()
	if sub._state == "auto":
		sub.Forward(15)
	if sub._state == "manual":
		sub.UpdateJoystick()

# time.sleep(4)

# connectionParent, connectionChild = Pipe()
# if __name__ == "__main__":
# 	controller = Controller_Operations.ControllerOps("blah", connectionChild)
#
# 	while True:
# 		if connectionParent.poll():
# 			message = connectionParent.recv()
# 			print(message)
