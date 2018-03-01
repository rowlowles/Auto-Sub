from DepthSensor import  *
from time import sleep
import time

fileOut = open("testCSV.csv","w")

sensor = DepthSensor()
numberOfDataPoints = 10000

for i in range(numberOfDataPoints):
	result = sensor.UpdateValue()
	fileOut.write(str(time.time()))
	fileOut.write(",")
	fileOut.write(str(result[0]))
	fileOut.write(",")
	fileOut.write(str(result[1]))
	fileOut.write("\n")
	if(not (i%1000)):
		print(i)
	
fileOut.close()