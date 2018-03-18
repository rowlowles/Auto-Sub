# Save as client.py
# Message Sender
import os
from socket import *
from multiprocessing import Pipe
from Pi_Code import Controller_Operations
import time

parent, child = Pipe()

host = "169.254.8.150" # My personal Pi that I was using for testing this script
#host = "169.254.14.48" # New pi we borrowed from Sasha's group
#host = "169.254.144.182" # ld Pi that went the way of the dinosaurs

port = 13000
addr = (host, port)
UDPSock = socket(AF_INET, SOCK_DGRAM)

if __name__ == "__main__":
	# Create the controller. Note: Must be done in "__main__" or it throws an error.
	controller = Controller_Operations.ControllerOps("", child)
	while True:
		if parent.poll():
			data = parent.recv()
			command = data.split(",")
			# At the moment we are not dealing with state changes, so just discard this
			if command[0] == "auto" or command[0] == "manual" or command[0] == "idle":
				command = str(command)
				print(command)

			# If it is a servo command convert it to these values
			elif command[0] == 'srv':
				angle = float(command[1])
				diveAng = angle <= 0  # Swap the greater than/less than sign to invert y-axis on the pitch
				command = "None,None,None,None,"+str(abs(angle))+","+str(diveAng)
				UDPSock.sendto(command.encode(), addr)

			# Otherwise this is a motor command and we go here.
			else:
				com0 = float(command[0])
				com1 = float(command[1])
				left_forward = com0 <= 0
				right_forward = com1 <= 0
				command = str(abs(com0))+","+str(left_forward)+","+ str(abs(com1))+","+ str(right_forward)+",None,None"
				UDPSock.sendto(command.encode(), addr)

			if command == "exit":
				break
	# data = input("Enter message to send or type 'exit': ")
	# UDPSock.sendto(data.encode(),addr)
	# if data == "exit":
	# 	break

	UDPSock.close()
	os._exit(0)
