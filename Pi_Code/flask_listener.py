import os
from socket import *
from multiprocessing import Process, Pipe

class portListener():
    def __init__(self, connection):
        # Initialize the socket listener and pipe.
        self.host = ""
        self.port = 13000
        self.buf = 1024
        self.addr = (self.host, self.port)
        self.UDPSock = socket(AF_INET, SOCK_DGRAM)
        self.UDPSock.bind(self.addr)
        print ("Waiting to receive messages...")
        p = Process(target=self.pollSocket, args= (connection,))
        p.start()

    def pollSocket(self, connection):
        print("here")
        while True:
            (data, addr) = self.UDPSock.recvfrom(self.buf)
            # Convert the received data from bytes to a string, then split it into a list of commands
            data = data.decode('utf-8')
            packet = data.split(",")

            # For each element in the received data, convert the value into either a Bool, a None, or a motor speed
            for index in range(len(packet)):
                if packet[index] == "True":
                    packet[index] = True
                elif packet[index] == "False":
                    packet[index] = False
                elif packet[index] == "None":
                    packet[index] = None
                else:
                    packet[index] = float(packet[index])

            # Send the packet to the parent pipe
            connection.send(packet)
            if (connection.poll()):
                break
        self.UDPSock.close()
        os._exit(0)