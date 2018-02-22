int encoder0PinA = 2;
int encoder0PinB = 3;
volatile int encoder0Pos = 0;
volatile int encoder0PinALast = LOW;
volatile int n = LOW;
int valNew = 0;
int valOld = 0;
int oldTime = 0;
int newTime = 0;
volatile int m = LOW;

void setup()
{
  pinMode (encoder0PinA,INPUT); 
  pinMode (encoder0PinB,INPUT);
  Serial.begin (38400);
  attachInterrupt(1, CountA, CHANGE);
  attachInterrupt(0, StateB, FALLING);
  newTime = micros();
}

void loop()
{
  encoder0PinALast = n;
  valNew = encoder0Pos;
  if (valNew != valOld) {
    newTime = micros();
    Serial.print (encoder0Pos, DEC); 
    Serial.print (",");
    Serial.print (newTime-oldTime, DEC);
    Serial.print (",");
    Serial.print (1000000 * float(valNew - valOld) / (newTime-oldTime) , DEC); 
    Serial.print ("\n");
    valOld = valNew;
    oldTime = newTime; 
  }

}

void CountA()
{
  n = digitalRead(encoder0PinA); 
  if ((encoder0PinALast == LOW) && (n == HIGH)) { 
    if (m == LOW) { 
      encoder0Pos--; 
    } 
    else { 
      encoder0Pos++; 
    } 
  }
}
void StateB()
{
  m = digitalRead(encoder0PinB);
}
