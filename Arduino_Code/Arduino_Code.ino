#include "SubMutex.h"
#include "Motor.h"
#include "IMU.h"

#define TO_INT(x) ((x) - '0')

// a String to hold incoming data
char inputString[10];
int pos = 0;

// whether the string is complete
bool stringComplete = false; 

// Create the required variables for the messageBoard
SubMutex* serialMutex = new SubMutex();

// Create the motors 
Motor LeftMotor  (2000,1550,1450,1000,"(LM)");
Motor RightMotor (2000,1550,1450,1000,"(RM)");
Motor ServoMotor (170,90,90,35,"(SM)");
  
// Create the IMU class 
IMU _IMU;

void SendMessage(String src)
{
  serialMutex->TakeMutex();
  Serial.print( "[Log]" + src +"\n");
  serialMutex->GiveMutex();
}

void setup()
{
  // Start the serial communication
  Serial.begin(38400);

  SendMessage("Started");

  // Allocate the pins for the motors
  LeftMotor.SetPin( 6 );
  RightMotor.SetPin( 5 );
  ServoMotor.SetPin( 3 );
  
  // Set up the required messaging variables
  LeftMotor.SetMessagingBoard(serialMutex);
  RightMotor.SetMessagingBoard(serialMutex);
  ServoMotor.SetMessagingBoard(serialMutex);
  _IMU.SetMessagingBoard(serialMutex);

  // Run the needed initialization for the IMU
  _IMU.Init();

  SendMessage("Done setup");
}

void loop()
{
  // Here is where all the message passing will occur
  // We need to both check if we have anything to write or anything to read

  while (Serial.available() && !stringComplete) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString[pos] = inChar;
    pos = pos + 1;
    if(pos == 10)
      pos = 0; // We have no better way of dealing with this rn
    
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }

  _IMU.updateIMU();
    
  if(stringComplete)
  {

    //Let's find out who we are talking too
    if(inputString[1] == 'M')
    {
      if(inputString[0] == 'L')
      {
        float inspeed = ((TO_INT(inputString[3]) * 100) + (TO_INT(inputString[4]) * 10) + TO_INT(inputString[5]) +  TO_INT(inputString[6])/10.0 + TO_INT(inputString[7])/100.0 )/100.0;
        // We are talking to the left motor
        if( inputString[2] == '+' )
        {
          // We want to move forward
          LeftMotor.SetSpeed(inspeed, true);
        }
        else if( inputString[2] == '-')
        {
         // We want to move backwards
          LeftMotor.SetSpeed(inspeed, false);
        }
        else
        {
          serialMutex->TakeMutex();
          Serial.print("[Log]No sign\n");
          serialMutex->GiveMutex();
        }
      }
      else if(inputString[0] == 'R')
      {
        float inspeed = ((TO_INT(inputString[3]) * 100) + (TO_INT(inputString[4]) * 10) + TO_INT(inputString[5]) +  TO_INT(inputString[6])/10.0 + TO_INT(inputString[7])/100.0 )/100.0;
        // We are talking to the left motor
        if( inputString[2] == '+' )
        {
          // We want to move forward
          RightMotor.SetSpeed(inspeed, true);
        }
        else if( inputString[2] == '-')
        {
         // We want to move forward
          RightMotor.SetSpeed(inspeed, false);
        }
        else
        {
          serialMutex->TakeMutex();
          Serial.print("[Log]No sign\n");
          serialMutex->GiveMutex();
        }
      }
      else if(inputString[0] == 'S')
      {
        float inspeed = (TO_INT(inputString[3]) * 100) + (TO_INT(inputString[4]) * 10) + TO_INT(inputString[5]);
        // We are talking to the left motor
        if( inputString[2] == '+' || inputString[2] == '-')
        {
          // We want to move forward
          ServoMotor.SetAngle(inspeed);
        }
        else
        {
          serialMutex->TakeMutex();
          Serial.print("[Log]No sign \n");
          serialMutex->GiveMutex();
        }
      }
    }
    else
    {
      serialMutex->TakeMutex();
      Serial.print("[Log]No motor\n");
      serialMutex->GiveMutex();
    }
    
    // Clear message once we are done with it
    stringComplete = false;
    pos = 0;    
  }//stringComplete

}

