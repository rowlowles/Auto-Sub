#include <Servo.h>

Servo motor;
int lowerBound = 35;
int upperBound = 175;

int pos = 0;    // variable to store the servo position

void setup() {
  Serial.begin(38400);
  motor.attach(6); 
  motor.write(lowerBound);
}

void loop() {
  for (pos = lowerBound; pos <= upperBound; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    motor.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
    Serial.print("We at : ");
    Serial.println(pos);
  }
  for (pos = upperBound; pos >= lowerBound; pos -= 1) { // goes from 180 degrees to 0 degrees
    motor.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
    Serial.print("We at : ");
    Serial.println(pos);
  }
}
