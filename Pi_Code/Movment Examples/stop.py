from MessageBoard import MessageBoard
from threading import Thread, Lock
from time import sleep
from Ptr import ptr
from Turn90DegreeCW import Turn90DegreeCW
from Submarine import *

# Create the board
board = MessageBoard()
sub = Submarine(board)

# Start the board
messageBoardThread = Thread(target=board.ReadSerial)
messageBoardThread.start()

sleep (2)

sub.SendLeftSpeedPacket(0,True)
sub.SendRightSpeedPacket(0,True)

sleep(3)

board.CloseBoard()
sub.ShutDown()