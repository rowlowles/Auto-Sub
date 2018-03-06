#from Submarine import *
from multiprocessing import Process
import pygame
import time

# Axes legend:
# Axes 0: Roll
# Axes 1: Pitch
# Axes 2: Throttle
# Axes 3: Yaw


class controllerOps:

    def __init__(self, dataFile, connection, SaveSensorData):
        pygame.joystick.init()
        screen = pygame.display.set_mode((10, 10))
        running = True
        clock = pygame.time.Clock()
        startTime = time.time()

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        # Get the properties of the joystick
        print("Found joystick: " + self.controller.get_name())
        buttons = self.controller.get_numbuttons()
        axes = self.controller.get_numaxes()
        balls = self.controller.get_numballs()
        hats = self.controller.get_numhats()
        p = Process(target = self.getStickPosition, args = (dataFile, connection, SaveSensorData))
        p.start()

    def getStickPosition(self, connection, dataFile, SaveSensorData ):
        read_stick = True

        while read_stick:
            # Update states
            pygame.event.pump()

            # Hardcoded for now, will fix later.
            threshhold = .3

            roll = self.controller.get_axis(0)
            pitch = self.controller.get_axis(1)
            throttle = self.controller.get_axis(2)
            # yaw = controller.get_axis(3) (Not used at the moment)
            trigger = self.controller.get_button(0)
            kill = self.controller.get_button(1)

            # Now that we have pitch/roll/throttle/yaw values, we can start using them
            # Send a tuple (x,y) where x and y are the speeds for the left and right motors respectively
            if kill:
                connection.send((0,0))

            elif trigger:
                # Set the speed to throttle and send both
                connection.send((throttle, throttle))

            elif abs(pitch) > threshhold:
                # Abs Max pitch is ~.6, and the max angle we should have for our fins is 20 deg (from Stubley)
                # Divide the pitch value by 3, so our min dive angle for our fins will be 10 deg, and max will be 20
                angle = pitch/3
                connection.send(angle)

            elif (not trigger) and (abs(roll) > threshhold):
                # Since we can't roll, I am mapping roll to yaw controls. Roll axis has better response on the joystick
                if roll > 0:
                    # If roll is positive, set the left motor to active and right to off
                    connection.send((throttle, 0))
                else:
                    # If roll is negative, set left to zero and right to active
                    connection.send((throttle, roll))
