from multiprocessing import Process,Pipe
from time import sleep 

class worker:
	def __init__(self, connection):
		self.p = Process(target=self.loop,args=(connection,))
		self.p.start()
		
	def loop(self,connection):
		i = 0
		while(True):
			i += 1
			connection.send(i)
			print("Sent")
			sleep(3)

if __name__ == '__main__': 
	parent_conn, child_conn = Pipe()
	src = worker(child_conn)

	
	while(True):
		if(parent_conn.poll()):
			print(parent_conn.recv()) 
		print("We still here")
		sleep(0.1)