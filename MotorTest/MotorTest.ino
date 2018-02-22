#include <Servo.h> 

Servo motor;
int wait = 1000;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(38400);
  motor.attach(6);
  motor.writeMicroseconds(1500);
}

void loop() {
  // put your main code here, to run repeatedly:
  for(int i = 0; i < 85; i ++)
  {
    Serial.print(String(1500 + i) + "\n");
    motor.writeMicroseconds(1500 + i);
    delay(wait/2);
  }
  motor.writeMicroseconds(1500);
  delay(wait * 2);
  
  for(int i = 0; i < 85; i ++)
  {
    Serial.print(String(1500 - i) + "\n");
    motor.writeMicroseconds(1500 - i);
    delay(wait/2);
  }
}
