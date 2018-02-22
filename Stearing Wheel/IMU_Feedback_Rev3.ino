/* SDA and SCL should have external pull-up resistors (to 3.3V).
 10k resistors are on the EMSENSR-9250 breakout board.

 Hardware setup:
 MPU9250 Breakout --------- Arduino
 VDD ---------------------- 3.3V
 VDDI --------------------- 3.3V
 SDA ----------------------- A4
 SCL ----------------------- A5
 GND ---------------------- GND
 */

#include "MPU9250.h"
#include "Filters.h"
#include <Servo.h>

Servo motor;
#define AHRS true         // Set to false for basic data read
#define SerialDebug false  // Set to true to get Serial output for debugging

//My controls:
double oldtime;
double newtime = 0;

double roll;
double pitch;
double yaw;

double calibtime = 5000;

double checkpoint0 = 0;
double checkpoint1 = 0;
double checkpoint2 = 0;

double sensitivity_thresh_0 = 0;
double sensitivity_thresh_1 = 0;
double sensitivity_thresh_2 = 0;

double IMU_time = 50;

int state = 0;

MPU9250 myIMU0(0);

FilterOnePole lowpassFilter0 ( LOWPASS, 10000000);
FilterOnePole lowpassFilter1 ( LOWPASS, 10000000);
FilterOnePole lowpassFilter2 ( LOWPASS, 10000000);

int wait = 50;

void rampDown_F()
{
  motor.write(94);
  delay(wait);
  motor.write(93);
  delay(wait);
  motor.write(92);
  delay(wait);
  motor.write(91);
  delay(wait);
  motor.write(90);
  delay(wait);
}

void rampDown_B()
{
  motor.write(86);
  delay(wait);
  motor.write(87);
  delay(wait);
  motor.write(88);
  delay(wait);
  motor.write(89);
  delay(wait);
  motor.write(90);
  delay(wait);
}

void rampUp_F()
{
  motor.write(91);
  delay(wait);
  motor.write(92);
  delay(wait);
  motor.write(93);
  delay(wait);
  motor.write(94);
  delay(wait);
  motor.write(95);
  delay(wait);
}

void rampUp_B()
{
  motor.write(89);
  delay(wait);
  motor.write(88);
  delay(wait);
  motor.write(87);
  delay(wait);
  motor.write(86);
  delay(wait);
  motor.write(85);
  delay(wait);
}

void setup()
{
  Serial.begin(38400);

  motor.attach(5); 
  motor.write(90);
  
#ifdef CHARMOTOR
  Serial.println("Going to start now");
  delay(wait);

  // write 500
  Serial.println("Writing 500");
  motor.write(180);
  delay(wait);

  // write 100
  Serial.println("Writing 100");
  motor.write(0);
  delay(wait);

  // write 300
  Serial.println("Writing 300");
  motor.write(135);
  delay(wait);

  // write 100
  Serial.println("Writing 100");
  motor.write(0);
  delay(wait);

  // write 200
  Serial.println("Writing 200");
  motor.write(90);
  delay(wait);
#endif 

  Serial.println("Serial Started");
  
  Wire.begin();

  Serial.println("Wire Started");
  
  // Read the WHO_AM_I register, this is a good test of communication
  
  byte c = myIMU0.readByte(myIMU0.MPU9250_ADDRESS, WHO_AM_I_MPU9250);

  Serial.println("I got this far");
  
  if (c == 0x71) // WHO_AM_I should always be 0x68
  {
    Serial.println("MPU9250 0 is online..."); 

    // Start by performing self test and reporting values
    myIMU0.MPU9250SelfTest(myIMU0.SelfTest);

    // Calibrate gyro and accelerometers, load biases in bias registers
    myIMU0.calibrateMPU9250(myIMU0.gyroBias, myIMU0.accelBias);

    myIMU0.initMPU9250();
    // Initialize device for active mode read of acclerometer, gyroscope, and
    // temperature
    Serial.println("MPU9250 initialized for active data mode....");

    // Read the WHO_AM_I register of the magnetometer, this is a good test of
    // communication


  } // if (c == 0x71)
  else
  {
    Serial.print("Could not connect to MPU9250 #0: 0x");
    Serial.println(c, HEX);
    while(1) ; // Loop forever if communication doesn't happen
  }
}

void loop()
{
  // If intPin goes high, all data registers have new data
  // On interrupt, check if data ready interrupt
  if (myIMU0.readByte(myIMU0.MPU9250_ADDRESS, INT_STATUS) & 0x01)
  {
    myIMU0.readGyroData(myIMU0.gyroCount);  // Read the x/y/z adc values
    myIMU0.getGres();

    // Calculate the gyro value into actual degrees per second
    // This depends on scale being set
    myIMU0.gx = (float)myIMU0.gyroCount[0]*myIMU0.gRes;
    myIMU0.gy = (float)myIMU0.gyroCount[1]*myIMU0.gRes;
    myIMU0.gz = (float)myIMU0.gyroCount[2]*myIMU0.gRes;

  } // if (readByte(myIMU.MPU9250_ADDRESS, INT_STATUS) & 0x01)
  
  // Must be called before updating quaternions!
  myIMU0.updateTime();

  if (!AHRS)
  {
    myIMU0.delt_t = millis() - myIMU0.count;
    if (myIMU0.delt_t > IMU_time)
    {
      myIMU0.count = millis();
    } // if (myIMU.delt_t > IMU_time)
  } // if (!AHRS)
  else
  {
    // Serial print and/or display at 0.5 s rate independent of data rates
    myIMU0.delt_t = millis() - myIMU0.count;

    // update LCD once per half-second independent of read rate
    if (myIMU0.delt_t > IMU_time)
    {
      myIMU0.count = millis();
      myIMU0.sumCount = 0;
      myIMU0.sum = 0;
    } // if (myIMU.delt_t > 500)
  } // if (AHRS)

  
  if ( millis() > 2000)
  {
    if (millis() < calibtime +2000)
    { 
      newtime = millis();
      checkpoint0 = checkpoint0 + (myIMU0.gx * (newtime-oldtime));
      checkpoint1 = checkpoint1 + (myIMU0.gy * (newtime-oldtime));
      checkpoint2 = checkpoint2 + (myIMU0.gz * (newtime-oldtime));
      
      oldtime = newtime;

      if (abs(myIMU0.gx) > sensitivity_thresh_0)
        sensitivity_thresh_0 = abs(myIMU0.gx);  
        
      if (abs(myIMU0.gy) > sensitivity_thresh_1)
        sensitivity_thresh_1 = abs(myIMU0.gy);  
        
      if (abs(myIMU0.gz) > sensitivity_thresh_2)
        sensitivity_thresh_2 = abs(myIMU0.gz);    
    }
    else
    {
      newtime = millis();

      if (abs(myIMU0.gx) > sensitivity_thresh_0*2)
      {
        roll = roll + ((myIMU0.gx - (checkpoint0/calibtime))*(newtime-oldtime))/1000;
        lowpassFilter0.input(roll);
      }
      if (abs(myIMU0.gy) > sensitivity_thresh_1*2)
      {
        pitch = pitch + ((myIMU0.gy - (checkpoint1/calibtime))*(newtime-oldtime))/1000;
        lowpassFilter1.input(pitch);
      }
      if (abs(myIMU0.gz) > sensitivity_thresh_2*2)
      {
        yaw = yaw + ((myIMU0.gz - (checkpoint2/calibtime))*(newtime-oldtime))/1000;
        lowpassFilter2.input(yaw);
      }
      
      Serial.print(" Roll : ");
      Serial.print(roll);
      Serial.print(" Pitch ");
      Serial.print(pitch);
      Serial.print(" Yaw : ");
      Serial.println(yaw);

      if(yaw > 5 && state == 0)
      {
        Serial.println("Ramping up forward");
        rampUp_F();
        state = 1;
      }
      else if( yaw < -5 && state == 0)
      {
        Serial.println("Ramping up backward");
        rampUp_B();
        state = 2;
      }
      else if( abs(yaw) < 5 && state == 1)
      {
        Serial.println("Breaking forward");
        rampDown_F();
        state = 0;
      }
      else if( abs(yaw) < 5 && state == 2)
      {
        Serial.println("Breaking backward");
        rampDown_B();
        state = 0;
      }
      oldtime = newtime;
        
     }    
  }
}
