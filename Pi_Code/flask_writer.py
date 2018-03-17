# Save as client.py
# Message Sender
import os
from socket import *
from multiprocessing import Pipe
from Pi_Code import Controller_Operations
import time

parent, child = Pipe()

#host = "169.254.8.150"
host = "169.254.14.48"
#host = "169.254.144.182" # set to IP address of target computer
port = 13000
addr = (host, port)
UDPSock = socket(AF_INET, SOCK_DGRAM)

if __name__ == "__main__":
	controller = Controller_Operations.ControllerOps("", child)
	while True:
		if parent.poll():
			data = parent.recv()
			command = data.split(",")
			if command[0] == "auto" or command[0] == "manual" or command[0] == "idle":
				command = str(command)
				print(command)

			elif command[0] == 'srv':
				angle = float(command[1])
				diveAng = angle <= 0
				command = "None,None,None,None,"+str(abs(angle))+","+str(diveAng)
				UDPSock.sendto(command.encode(), addr)

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
