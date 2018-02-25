/*
*Quadrature Decoder 
*/
#include "Arduino.h"
#include "digitalWriteFast.h"  // library for high performance reads and writes by jrraines
                               // see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1267553811/0
                               // and http://code.google.com/p/digitalwritefast/
#include <Servo.h>

// It turns out that the regular digitalRead() calls are too slow and bring the arduino down when
// I use them in the interrupt routines while the motor runs at full speed.

// Quadrature encoders
// Left encoder
#define c_LeftEncoderInterruptA 0
#define c_LeftEncoderInterruptB 1
#define c_LeftEncoderPinA 2
#define c_LeftEncoderPinB 3
#define c_MotorPin 6
#define LeftEncoderIsReversed

/* 
 *  Yellow ESC -> Signal (pin 6)
 *  Middde ESC -> NC
 *  Brown ESC -> Ground (GND)
 */

#define TICKS_PER_REV 2000.0
#define US_TO_S 1000000

double oldTime = 0.0;
double newTime = 0.0;
double startTime = 0.0;

int steps = 0;
int counter = 0; 
int oldValue = 0;
int newValue = 0;

volatile bool _LeftEncoderASet;
volatile bool _LeftEncoderBSet;
volatile bool _LeftEncoderAPrev;
volatile bool _LeftEncoderBPrev;
volatile long _LeftEncoderTicks = 0;


Servo _motor;

void setup()
{
  Serial.begin(38400);

  // Quadrature encoders
  // Left encoder
  pinMode(c_LeftEncoderPinA, INPUT);      // sets pin A as input
  digitalWrite(c_LeftEncoderPinA, LOW);  // turn on pullup resistors
  pinMode(c_LeftEncoderPinB, INPUT);      // sets pin B as input
  digitalWrite(c_LeftEncoderPinB, LOW);  // turn on pullup resistors
  attachInterrupt(c_LeftEncoderInterruptA, HandleLeftMotorInterruptA, CHANGE);
  attachInterrupt(c_LeftEncoderInterruptB, HandleLeftMotorInterruptB, CHANGE);
  oldTime = micros();
  Serial.print("Encoder Ticks,Revolutions,Speed [Ticks/s]\n");
  _motor.attach(c_MotorPin);
  _motor.write(90);
  delay(2000);
  startTime = micros();
}

void loop()
{
  if(micros() - startTime < 5*1000000)
  {
    Serial.print(micros());
    Serial.print(",");
    _motor.writeMicroseconds(1500);
    newValue = _LeftEncoderTicks;
    newTime  = micros();
    Serial.print(_LeftEncoderTicks);
    Serial.print(",");
    Serial.print(_LeftEncoderTicks/TICKS_PER_REV);
    Serial.print(",");
    Serial.print(US_TO_S * (newValue - oldValue)/(newTime - oldTime));
    Serial.print(",\n");
    oldValue = newValue;
    oldTime  = newTime; 
  }
  else
  {
    _motor.write(0);
    Serial.print("Done\n");
    for(;;)
    {
      delay(1000);
    }
  }
}


// Interrupt service routines for the left motor's quadrature encoder
void HandleLeftMotorInterruptA(){
  _LeftEncoderBSet = digitalReadFast(c_LeftEncoderPinB);
  _LeftEncoderASet = digitalReadFast(c_LeftEncoderPinA);
  
  _LeftEncoderTicks+=ParseEncoder();
  
  _LeftEncoderAPrev = _LeftEncoderASet;
  _LeftEncoderBPrev = _LeftEncoderBSet;
}

// Interrupt service routines for the right motor's quadrature encoder
void HandleLeftMotorInterruptB(){
  // Test transition;
  _LeftEncoderBSet = digitalReadFast(c_LeftEncoderPinB);
  _LeftEncoderASet = digitalReadFast(c_LeftEncoderPinA);
  
  _LeftEncoderTicks+=ParseEncoder();
  
  _LeftEncoderAPrev = _LeftEncoderASet;
  _LeftEncoderBPrev = _LeftEncoderBSet;
}

int ParseEncoder(){
  if(_LeftEncoderAPrev && _LeftEncoderBPrev){
    if(!_LeftEncoderASet && _LeftEncoderBSet) return 1;
    if(_LeftEncoderASet && !_LeftEncoderBSet) return -1;
  }else if(!_LeftEncoderAPrev && _LeftEncoderBPrev){
    if(!_LeftEncoderASet && !_LeftEncoderBSet) return 1;
    if(_LeftEncoderASet && _LeftEncoderBSet) return -1;
  }else if(!_LeftEncoderAPrev && !_LeftEncoderBPrev){
    if(_LeftEncoderASet && !_LeftEncoderBSet) return 1;
    if(!_LeftEncoderASet && _LeftEncoderBSet) return -1;
  }else if(_LeftEncoderAPrev && !_LeftEncoderBPrev){
    if(_LeftEncoderASet && _LeftEncoderBSet) return 1;
    if(!_LeftEncoderASet && !_LeftEncoderBSet) return -1;
  }
}

