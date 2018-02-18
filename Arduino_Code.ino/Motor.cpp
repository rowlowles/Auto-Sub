#include "Motor.h"

Motor::Motor(int maxForward, int stopValue, int maxReverse, String name)
{
  _maxForward = maxForward;
  _maxReverse = maxReverse;
  _stopValue  = stopValue;
  _currentSpeed = stopValue;

  _motor = Servo();

  _Logger = new MessageMaker(name,"Log");
  _Acknowledger = new MessageMaker(name, "Acknowledgment"); 
}

void Motor::Forward(bool ack = false)
{
  // To protect equipment and our sub, forward should only be 50% of our maximum allowable speed 
  int forwardSpeed = ((_maxForward - _stopValue) * 0.5 ) + _stopValue;

  if(_currentSpeed > forwardSpeed || _currentSpeed > _stopValue)
  {
    // We just need to slow down or speed up, shouldn't need to ramp because we are already going in the right direction
    _motor.write(forwardSpeed);
    _currentSpeed = forwardSpeed;
    SendMessage(String("Set speed to forward"), ack);
  }
  else
  {
    // We are stalled or in the wrong direction, ramp up from the current speed
    int numberOfSteps = (forwardSpeed - _currentSpeed);
    for(int i = 0; i < numberOfSteps; i++)
    {
      _motor.write(_currentSpeed + i);
      delay(MOTOR_RAMP_DELAY);
    }
    SendMessage("Ramped speed up to forward", ack);
  }
}

void Motor::Reverse(bool ack = false)
{
  // To protect equipment and our sub, reverse should only be 50% of our maximum allowable speed 
  int reverseSpeed = ((_stopValue - _maxReverse) * 0.5 ) + _maxReverse;

  if(_currentSpeed < reverseSpeed || _currentSpeed < _stopValue)
  {
    // We just need to slow down or speed up, shouldn't need to ramp because we are already going in the right direction
    _motor.write(reverseSpeed);
    _currentSpeed = reverseSpeed;
    SendMessage("Set speed to reverse", ack);
  }
  else
  {
    // We are stalled or in the wrong direction, ramp up from the current speed
    int numberOfSteps = (_currentSpeed - reverseSpeed);
    for(int i = 0; i < numberOfSteps; i++)
    {
      _motor.write(_currentSpeed - i);
      delay(MOTOR_RAMP_DELAY);
    }
    SendMessage("Ramped speed up to reverse", ack);
  }
}

void Motor::SetSpeed (int speed, bool ack = false)
{
  if(speed < _maxForward && speed > _maxReverse)
  {
    SendMessage("Set speed to : " + speed, ack);
  }
  else
  {
    SendMessage("Unable to set speed to : " + speed, ack);
  }
}

void Motor::SetPin(int pinNumber)
{
  _motor.attach(pinNumber);
}


void Motor::SetMessagingBoard (SemaphoreHandle_t mutex, Queue<String>* messageBoard)
{
  _messageBoard = messageBoard;
  _messageBoardMutex = mutex;
}

void Motor::SendMessage (String src, bool ack)
{
  xSemaphoreTake(_messageBoardMutex,0);
  _messageBoard->enqueue(_Logger->MakeMessage(src));
  if(ack)
  {
    _messageBoard->enqueue(_Acknowledger->MakeMessage(""));
  }
   xSemaphoreGive(_messageBoardMutex);
}

void Motor::CalibrateMotor()
{
  int wait = 2000; // 2 Second wait
  SendMessage(_Logger.MakeMessage("Going to start calibration"), false);
  delay(wait);

  SendMessage(_Logger.MakeMessage("Writing top speed"), false);
  _motor.write(180);
  delay(wait);

  // write 100
  SendMessage(_Logger.MakeMessage("Writing low speed"), false);
  _motor.write(0);
  delay(wait);

  // write 300
  SendMessage(_Logger.MakeMessage("Writing high middle speed"), false);
  _motor.write(135);
  delay(wait);

  // write 100
  SendMessage(_Logger.MakeMessage("Writing low speed"), false);
  _motor.write(0);
  delay(wait);

  // write 200
  SendMessage(_Logger.MakeMessage("Writing stop  speed"), false);
  _motor.write(90);
  delay(wait);
}