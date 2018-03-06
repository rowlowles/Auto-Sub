#from Submarine import *
from multiprocessing import process
import pygame
import time
# import csv
# import matplotlib.pyplot as plt


pygame.joystick.init()
screen = pygame.display.set_mode((10, 10))
running = True
clock = pygame.time.Clock()
startTime = time.time()

# Axes legend:
# Axes 0: Roll
# Axes 1: Pitch
# Axes 2: Throttle
# Axes 3: Yaw
joystickMotion=[]
while True:
    controller = pygame.joystick.Joystick(0)
    controller.init()

    print(controller.get_name())

    buttons = controller.get_numbuttons()
    axes = controller.get_numaxes()
    balls = controller.get_numballs()
    hats = controller.get_numhats()

    while time.time() - startTime < 10:
        # We need to pump() the events to get new positions for the axes
        # pygame.event.pump()
        #
        # controller.get_axis(0)
        # controller.get_axis(1)
        # controller.get_axis(2)
        # controller.get_axis(3)

        for event in pygame.event.get():
            axesVals = [0,0,0,0]

            if event.type == pygame.JOYAXISMOTION:
                axesVals[event.dict['axis']] = event.dict['value']
                joystickMotion.append(axesVals)

                #joystickMotion[event.dict['axis']].append(event.dict['value'])
            if event.type == pygame.JOYBUTTONDOWN:
                 print("Button down: " + str(event.dict))

    break

# axe0 = []
# axe1 = []
# axe2 = []
# axe3 = []
#
# for event in joystickMotion:
#     axe0.append(event[0])
#     axe1.append(event[1])
#     axe2.append(event[2])
#     axe3.append(event[3])
#
# fig, ((ax0,ax1),(ax2,ax3)) = plt.subplots(2,2)
# fig.subplots_adjust(top=0.92, left=0.07, right=0.97,
#                     hspace=0.3, wspace=0.3)
# ax0.plot(axe0)
# ax0.set_title('Roll')
# ax1.plot(axe1)
# ax1.set_title('Pitch')
# ax2.plot(axe2)
# ax2.set_title('Throttle')
# ax3.plot(axe3)
# ax3.set_title('Yaw')
# plt.show()

# with open('joystick'+ str(startTime)+ '.csv', 'w', newline = '') as csvfile:
#     spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
#     spamwriter.writerows(joystickMotion)

class controller_Ops:
    def __init__(self, dataFile, connection, SaveSensorData):
        controller = pygame.joystick.Joystick(0)
        controller.init()

        print("Found joystick: " + controller.get_name())

        buttons = controller.get_numbuttons()
        axes = controller.get_numaxes()
        balls = controller.get_numballs()
        hats = controller.get_numhats()

    def getStickPosition(self):
        pygame.event.pump()

        roll = controller.get_axis(0)
        pitch = controller.get_axis(1)
        throttle = controller.get_axis(2)
        yaw = controller.get_axis(3)
        motion = controller.get_button(0)

        #Now that we have pitch/roll/throttle/yaw values, we can start using them
