/*
The purpose of this class is to provide a common interface for the motors that will be used in this project, this class should accept serial messages and be able to parse them to determine the right action   
 */

#ifndef SUB_MOTOR_H
#define SUB_MOTOR_H

// Standard Libraries
#include <Servo.h>

// Custom Libraries
#include "Constants.h"
#include "Queue.h"
#include "SubMutex.h"

class Motor
{
  public:

  // The constructor of the Motor class
  // maxForward : The maximum allowable forward PWM
  // upperStopValue  : The PWM value to stop the motor (higher bound)
  // lowerStopValue  : The PWM value to stop the motor (lower bound)
  // maxReverse : The maximum allowable reverse PWM
  Motor(int maxForward, int upperStopValue, int lowerStopValue, int maxReverse, String Name);
  
  // Sets the motor to a set speed
  // This method logs an error if the requested speed is not allowable
  // This method sends an acknowledgment if requested
  void SetSpeed (float Speed, bool forward);
  
  // This method sets the pin that the motor is connected too
  void SetPin(int pinNumber);

  // This method gives the class a method of posting messages to the message board
  void SetMessagingBoard (SubMutex* mutex);

  // This method wraps the methods for sending a message to the message board
  void SendMessage ();

  private:
  int _maxForward;
  int _upperStopValue;
  int _lowerStopValue;
  int _maxReverse;
  int _pin;
  int _currentSpeed;
  String _name;
  String _message;

  Servo _motor;
  SubMutex* _messageBoardMutex;

};  // class Motor

#endif // SUB_MOTOR_H

