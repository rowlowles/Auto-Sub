#include "Motor.h"

Motor::Motor(int maxForward, int upperStopValue, int lowerStopValue, int maxReverse, String Name)
{
  _maxForward = maxForward;
  _maxReverse = maxReverse;
  _upperStopValue  = upperStopValue;
  _lowerStopValue  = lowerStopValue;
  _currentSpeed = upperStopValue;
  _name = Name;
  _message.reserve(15);
}

void Motor::SetSpeed (float Speed, bool Forward)
{
  if(Speed > 1)
    Speed = 1;

  if(Forward)
  {
    _currentSpeed = _upperStopValue + (_maxForward - _upperStopValue) * Speed;
    _motor.writeMicroseconds(_currentSpeed);
  }
  else
  {
    _currentSpeed = _lowerStopValue - (_lowerStopValue - _maxReverse) * Speed;
    _motor.writeMicroseconds(_currentSpeed);
  }
    
  _message = _currentSpeed;
  SendMessage(); 
}

void Motor::SetAngle (int angle)
{
  if(angle > _maxForward)
    angle = _maxForward;
  if(angle < _maxReverse)
    angle = _maxReverse;
  
  _motor.write(angle);
  _message = _currentSpeed;
  SendMessage(); 
}

void Motor::SetPin(int pinNumber)
{
  _motor.attach(pinNumber);
  _currentSpeed = (_lowerStopValue+_upperStopValue)/2.0;
  _motor.write(_currentSpeed);
}

void Motor::SetMessagingBoard (SubMutex* mutex)
{
  _messageBoardMutex = mutex;
}

void Motor::SendMessage ()
{
  _messageBoardMutex->TakeMutex();
  Serial.print("[Log]");
  Serial.print(_message);
  Serial.print(_name); 
  Serial.print("\n"); 
  _messageBoardMutex->GiveMutex();
}

