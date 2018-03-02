import serial
from time import sleep

ser = serial.Serial('/dev/ttyACM0',38400)

sleep(2)
print(ser.readline())
print(ser.readline())
print(ser.readline())
print(ser.readline())

ser.write(b'LM+05000\n')
ser.write(b'RM-05000\n')

print(ser.readline())
print(ser.readline())

sleep(10)

ser.write(b'LM+00000\n')
ser.write(b'RM+00000\n')

print(ser.readline())
print(ser.readline())