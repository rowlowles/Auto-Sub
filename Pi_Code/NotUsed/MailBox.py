from threading import Thread, Lock
from queue import Queue

EMPTY_MESSAGE = -1

class MailBox:
	def __init__(self):
		# Set up a FIFO queue to handle incoming messages
		self._inbox = Queue()
		# Set up a Mutex to protect the mailbox queue
		self._lock = Lock()
	
	# Allow a reader to get the oldest message, else return an EMPTY_MESSAGE 
	def GetMessage(self):
		self._lock.acquire()
		if(not self._inbox.empty()):
			message = self._inbox.get()
			self._lock.release()
			return message
		else:
			self._lock.release()
			return EMPTY_MESSAGE
	
	# Allow a sender to leave a message in the inbox
	def PutMessage(self,item):
		self._lock.acquire()
		self._inbox.put(item)
		self._lock.release()