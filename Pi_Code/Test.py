from multiprocessing import Pipe
from flask_listener import *

connectionParent, connectionChild = Pipe()

server = portListener(connectionChild)

while True:
	if connectionParent.poll():
		message = connectionParent.recv()
		print(message)
