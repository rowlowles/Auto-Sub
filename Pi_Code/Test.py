from Pi_Code import Controller_Operations#, Submarine
from multiprocessing import Pipe, process
#import time
import paramiko
import subprocess
import socket
import requests
# 192.168.1.121
# 169.254.8.150

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect(hostname= "raspberrypi.local",port = 22, username="pi", password='raspberry')


# sshProcess = subprocess.Popen(['ssh', "pi@192.168.1.121","ls"], shell=True,
# 							  stdout= subprocess.PIPE, stderr=subprocess.PIPE)

# stdin,stdout,stderr = ssh.exec_command('cd Desktop/PycharmProjects/Auto-Sub/Pi_Code; sudo python3 Test.py')#sshProcess.stdout.readlines()
# stdin.write('Sudo password:')
# stdin.flush()
# print(stdout.readlines())
# print(stderr.readlines())

# time.sleep(5)
#
# sub = Submarine.Submarine(False)
#
# while True:
#
# 	if sub._state == "idle":
# 		sub.UpdateJoystick()
# 	if sub._state == "auto":
# 		sub.Forward(15)
# 	if sub._state == "manual":
# 		sub.UpdateJoystick()

# time.sleep(4)

url = 'http://169.254.8.150:5000/display'
connectionParent, connectionChild = Pipe()
if __name__ == "__main__":
	controller = Controller_Operations.ControllerOps("blah", connectionChild)
	count = 0
	while count<50:
		if connectionParent.poll():
			message = connectionParent.recv()
			print(message)
			data = [('line',message),]
			re = requests.post(url, data)
			count+=1
	print("end")