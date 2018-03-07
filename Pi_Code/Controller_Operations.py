from multiprocessing import Process
import pygame

# Axes legend:
# Axes 0: Roll (right is positive, left is negative)
# Axes 1: Pitch (back is positive, forward is negative)
# Axes 2: Throttle (0% position is positive, 100% position is negative)
# Axes 3: Yaw (clockwise is positive, counterclockwise is negative)
# Button legend:
# Button 0: Trigger
# Button 6: Labelled as 07 on the joystick
# Button 5: Labelled as 06 on the joystick
# Button 1: Labelled as 02 on the joystick


class ControllerOps:

    def __init__(self, dataFile, connection, SaveSensorData):
        # We need to display a window in order to read joystick inputs.
        pygame.joystick.init()
        screen = pygame.display.set_mode((10, 10))

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.idle = True
        self.read_stick = True
        self.autosub = True

        dataFile.write("Found joystick: " + self.controller.get_name())

        p = Process(target = self.getStickPosition, args = (dataFile, connection, SaveSensorData))
        p.start()


    def getStickPosition(self, connection, dataFile, SaveSensorData):
        readController = True
        while (readController):

            while self.idle:
                # Start button code. Hold in idle until button 6 is pressed, and then send the response to the main loop
                pygame.event.pump()
                start = self.controller.get_button(6)
                if start:
                    connection.send("auto")
                    self.idle = False

            while self.autosub:
                # If we press button 5, we will switch to manual controls.
                # Otherwise, it will just keep looping in here.
                pygame.event.pump()
                manual = self.controller.get_button(5)
                if manual:
                    connection.send("manual")
                    self.autosub = False
                    self.read_stick = True

            while self.read_stick:
                # Update states
                pygame.event.pump()

                # Hardcoded for now, will fix later.
                threshhold = .3

                roll = self.controller.get_axis(0)
                pitch = self.controller.get_axis(1)
                throttle = (self.controller.get_axis(2))*100
                # yaw = controller.get_axis(3) (Not used at the moment)
                trigger = self.controller.get_button(0)
                stop = self.controller.get_button(6)
                kill = self.controller.get_button(1)
                auto_revert = self.controller.get_button(5)

                # Now that we have pitch/roll/throttle/yaw values, we can start using them
                # Send a tuple (x,y) where x and y are the speeds for the left and right motors respectively

                if kill:
                    # Shut down both the motors
                    connection.send((0, 0))

                if trigger:
                    # Set the speed to throttle and sent it to both motors
                    connection.send((throttle, throttle))

                if abs(pitch) > threshhold:
                    # |Max pitch| is ~.6, and the max angle we should have for our fins is 20 deg (from Stubley)
                    # Divide the pitch value by 3, so our min dive angle for our fins will be 10 deg, and max will be 20
                    angle = pitch/3
                    connection.send(angle)

                if (not trigger) and (abs(roll) > threshhold):
                    # Since we can't roll, I am mapping roll to yaw controls. Roll axis has better response on the joystick
                    if roll > 0:
                        # If roll is positive, set the left motor to active and right to off
                        connection.send((throttle, 0))
                    else:
                        # If roll is negative, set left to zero and right to active
                        connection.send((0, throttle))

                if auto_revert:
                    # If we press button 5, revert to automatic controls.
                    connection.send("auto")
                    self.autosub = True
                    break

                if stop:
                    connection.send("stop")
                    self.idle = True
                    break

            if (connection.poll()):
                readController = connection.recv()
                dataFile.close()