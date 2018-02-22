#include <Servo.h>

Servo _motor;

void CalibrateMotor()
{
  int wait = 3000; // 2 Second wait
  Serial.print("Going to start calibration\n");
  delay(wait);

  Serial.print("Writing top speed\n");
  _motor.writeMicroseconds(2000);
  delay(wait);

  // write 100
  Serial.print("Writing low speed\n");
  _motor.writeMicroseconds(1000);
  delay(wait);

  // write 300
  Serial.print("Writing high middle speed\n");
  _motor.writeMicroseconds(1750);
  delay(wait);

  // write 100
  Serial.print("Writing low speed\n");
  _motor.write(1000);
  delay(wait);

  // write 200
  Serial.print("Writing stop  speed\n");
  _motor.writeMicroseconds(1500);
  delay(wait);
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(38400);

  _motor.attach(6);

  CalibrateMotor();
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(100);
}
