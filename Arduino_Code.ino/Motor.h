/*
The purpose of this class is to provide a common interface for the motors that will be used in this project, this class should accept serial messages and be able to parse them to determine the right action   
 */

#ifndef SUB_MOTOR_H
#define SUB_MOTOR_H

// Standard Libraries
#include <Servo.h>

// Custom Libraries
#include "MessageMaker.h"
#include "Constants.h"
#include "Queue.h"

// External Libraries
#include "Arduino_FreeRTOS.h"
#include <semphr.h> 

class Motor
{
  public:

  // The constructor of the Motor class
  // maxForward : The maximum allowable forward PWM
  // stopValue  : The PWM value to stop the motor
  // maxReverse : The maximum allowable reverse PWM
  Motor(int maxForward, int stopValue, int maxReverse, String Name);
  
  // Sets the motor to its maximum forward speed
  // This method sends an acknowledgment if requested
  void Forward(bool ack = false);

  // Sets the motor to its maximum reverse speed
  // This method sends an acknowledgment if requested
  void Reverse(bool ack = false);
  
  // Sets the motor to a set speed
  // This method logs an error if the requested speed is not allowable
  // This method sends an acknowledgment if requested
  void SetSpeed (int speed, bool ack = false);
  
  // This method sets the pin that the motor is connected too
  void SetPin(int pinNumber);

  // This method gives the class a method of posting messages to the message board
  void SetMessagingBoard (SemaphoreHandle_t mutex,Queue<String>* messageBoard);

  // This method wraps the methods for sending a message to the message board
  void SendMessage (String src, bool ack);

  // This method runs the calibration for the motor ESC's  
  void CalibrateMotor ();

  private:
  int _maxForward;
  int _stopValue;
  int _maxReverse;
  int _pin;
  int _numberOfRampSteps;
  int _currentSpeed;

  Servo _motor;
  MessageMaker* _Logger;
  MessageMaker* _Acknowledger;
  SemaphoreHandle_t _messageBoardMutex;
  Queue<String>* _messageBoard; 

};  // class Motor

#endif // SUB_MOTOR_H
