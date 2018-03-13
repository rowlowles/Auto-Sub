import requests
import time
import sys
from multiprocessing import Pipe
from Pi_Code import Controller_Operations

# Url must be in format of `http://xxx.xxx.xxx.xxx:5000/display` where xxx.xxx.xxx.xxx is the Pi's IP address

url = 'http://169.254.8.150:5000/display'
# Setup a pipe between here and the controller
connectionParent, connectionChild = Pipe()

def sendMessage(url, data):
	for i in range (0,5):
		try:
			requests.post(url, data)
			return
		except:
			print("Failed to send, retrying")
			time.sleep(1)

	print("Repeated failed posts. Shutting down")
	connectionParent.send(False)
	sys.exit(1)

if __name__ == "__main__":
	controller = Controller_Operations.ControllerOps("", connectionChild)
	while True:
		if connectionParent.poll():
			# Message is one of three formats:
			# text string with value "auto","manual","idle" (used to set submarine state)
			# string in format `srv,xx` where xx is the servo angle
			# string in format `xx,yy` where xx and yy are the speeds for each motor
			message = connectionParent.recv()
			#print(message)
			data = [('line',message),]
			sendMessage(url, data)
