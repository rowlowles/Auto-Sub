from multiprocessing import Process
import pygame
import time

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

    def __init__(self, dataFile, connection):
        # We need to display a window in order to read joystick inputs.
        # dataFile.write("Found joystick: " + self.controller.get_name() + "\n")
        p = Process(target=self.getStickPosition, args=(dataFile, connection))
        p.start()

    def getStickPosition(self, dataFile, connection):
        pygame.joystick.init()
        # Pygame needs a screen to read joystick values
        screen = pygame.display.set_mode((10, 10))

        # Initialize the joystick
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.state = "idle"
        readController = True
        while readController:

            if self.state == "idle":
                # Start button code. Hold in idle until button 6 is pressed, and then send the response to the main loop
                pygame.event.pump()
                start = self.controller.get_button(6)
                if start:
                    connection.send("auto")
                    self.state = "auto"

            if self.state == "auto":
                # If we press button 5, we will switch to manual controls.
                # Otherwise, it will just keep looping in here.
                pygame.event.pump()
                manual = self.controller.get_button(5)
                if manual:
                    connection.send("manual")
                    self.state = "manual"
                    while manual:
                        pygame.event.pump()
                        manual = self.controller.get_button(5)

            if self.state == "manual":
                # Update states
                pygame.event.pump()
                # Hardcoded threshold values
                threshhold = .2
                maxValApprox = .8

                roll = self.controller.get_axis(0)
                pitch = self.controller.get_axis(1)
                # Convert the throttle values from ~(-0.7 <-> 0.5) to (0 <-> 45)
                throttle = (((self.controller.get_axis(2)+.7)/1.2)*45)-3
                if throttle < 5:
                    throttle = 0
                if throttle > 40:
                    throttle = 45

                # yaw = controller.get_axis(3) (Not used at the moment)
                trigger = self.controller.get_button(0)
                # stop = self.controller.get_button(6)
                kill = self.controller.get_button(1)
                # auto_revert = self.controller.get_button(5)

                # Now that we have pitch/roll/throttle/yaw values, we can start using them
                # Send a string "x,y" where x and y are the speeds for the left and right motors respectively
                if kill:
                    # Shut down both the motors and set the servo to zero
                    connection.send("0, 0")
                    connection.send("srv,0")
                    time.sleep(1)

                if trigger:
                    # Set the speed to throttle and sent it to both motors
                    connection.send(str(throttle)+','+str(throttle))

                if abs(pitch) > threshhold:
                    # |Max pitch| is ~.6, and the max angle we should have for our fins is 20 deg (from Stubley)
                    # Divide the pitch value by 3, so our min dive angle for our fins will be 10 deg, and max will be 20
                    angle = pitch/3
                    connection.send("srv,"+str(angle*100))

                if (not trigger) and (abs(roll) > threshhold):
                    # Since we can't roll, I am mapping roll to yaw controls. Roll axis has better signals
                    # The more the joystick is moved, the faster the turn speed
                    # Scales from ~50% to ~0% speed on the opposite motor
                    turnSpeed = (abs((abs(roll)-maxValApprox))*throttle)
                    if turnSpeed < 10:
                        turnSpeed = 0
                    if roll > 0:
                        # If roll is positive, set the left motor to active and right to off
                        connection.send(str(throttle)+','+str(turnSpeed))
                    else:
                        # If roll is negative, set left to zero and right to active
                        connection.send(str(turnSpeed)+','+ str(throttle))

                # Commented out because we currently don't want to go back to auto after going to manual
                # if auto_revert:
                #     # If we press button 5, revert to automatic controls.
                #     connection.send("auto")
                #     self.state = "auto"
                #     while auto_revert:
                #         # Wait for button to be released
                #         pygame.event.pump()
                #         auto_revert = self.controller.get_button(5)
                #     break
				#
                # if stop:
                #     connection.send("idle")
                #     self.state = "idle"
                #     while stop:
                #         # Wait for button to be released
                #         pygame.event.pump()
                #         stop = self.controller.get_button(6)
                #     break

                # Clear the event queue so we don't have a long backlog of events that we need to send to the Pi
                pygame.event.clear()
                time.sleep(.01)

            if (connection.poll()):
                readController = connection.recv()
                dataFile.close()
