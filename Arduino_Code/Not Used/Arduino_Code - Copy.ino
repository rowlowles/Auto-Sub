#include <Arduino_FreeRTOS.h>
#include <semphr.h> 

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

#include "Queue.h"
#include "Motor.h"
#include "IMU.h"

String inputString = "";  // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

// Creates the message board logger
MessageMaker logger("Arduino","Log");

// Create the required variables for the messageBoard
SemaphoreHandle_t xSemaphore = xSemaphoreCreateMutex();
Queue<String> messageBoard; 

// Create the motors 
Motor LeftMotor  (95,90,85,"LeftMotor");
Motor RightMotor (95,90,85,"RightMotor");
Motor ServoMotor (175,35,90,"ServoMotor");
  
// Create the IMU class 
IMU _IMU;
  
void setup()
{
  // Start the serial communication
  Serial.begin(38400);

  for(;;)
  {
    //Serial.write(logger.MakeMessage("Started Serial").c_str()); 
    Serial.write("Fuck"); 
  }
  
  // Allocate the pins for the motors
  LeftMotor.SetPin( 6 );
  RightMotor.SetPin( 5 );
  ServoMotor.SetPin( 3 );

  Serial.write(logger.MakeMessage("Set Motor pins").c_str());

  // Set up the required messaging variables
  LeftMotor.SetMessagingBoard(xSemaphore, &messageBoard);
  RightMotor.SetMessagingBoard(xSemaphore, &messageBoard);
  ServoMotor.SetMessagingBoard(xSemaphore, &messageBoard);
  _IMU.SetMessagingBoard(xSemaphore, &messageBoard);

  Serial.write(logger.MakeMessage("Set Motor pins").c_str());

  // Run the needed initialization for the IMU
  _IMU.Init();

  // Create a thread to monitor the IMU data 
  xTaskCreate(
    _IMU.Loop,        /* Task function. */
    "IMUThread",      /* String with name of task. */
    10000,            /* Stack size in words. */
    &(_IMU),             /* Parameter passed as input of the task */
    1,                /* Priority of the task. */
    NULL);            /* Task handle. */

}

void loop()
{
  // Here is where all the message passing will occur
  // We need to both check if we have anything to write or anything to read

  // String complete is our sign that we got a messages
  if (stringComplete) {
    // Do something with the message
    
    int endOfHeader = inputString.indexOf(']');
    if( endOfHeader != -1)
    {
      String header = inputString.substring(0, endOfHeader);
      if(header.equals("IMU"))
      {
        Serial.write( logger.MakeMessage("IMU Message received, no currently supported IMU commands exist").c_str() );
      } 
      else if (header.equals("LeftMotor") || header.equals("RightMotor") || header.equals("ServoMotor"))
      {
        int endOfMessage = inputString.indexOf('(');
        if(endOfMessage != -1)
        {
          String message = inputString.substring(endOfHeader + 1, endOfMessage -1);
          bool ack = (inputString.substring(endOfMessage, inputString.length() - 2)).equals("True");
          if(message.equals(String('F')))
          {
            if(header.equals("LeftMotor"))
            {
              LeftMotor.Forward(ack);
            }
            else if(header.equals("RightMotor"))
            {
              RightMotor.Forward(ack);
            }
            else if (header.equals("ServoMotor"))
            {
              ServoMotor.Forward(ack);
            }
          }
          else if (message.equals(String('R')))
          {
            if(header.equals("LeftMotor"))
            {
              LeftMotor.Reverse(ack);
            }
            else if(header.equals("RightMotor"))
            {
              RightMotor.Reverse(ack);
            }
            else if (header.equals("ServoMotor"))
            {
              ServoMotor.Reverse(ack);
            }
          }
          else if (message.equals(String('S')))
          {
            if(header.equals("LeftMotor"))
            {
              LeftMotor.SetSpeed(LeftMotor.StopValue(), ack);
            }
            else if(header.equals("RightMotor"))
            {
              RightMotor.SetSpeed(RightMotor.StopValue(), ack);
            }
            else if (header.equals("ServoMotor"))
            {
              ServoMotor.SetSpeed(ServoMotor.StopValue(), ack);
            }
          }
          else
          {
            // Assume we received an integer value
            int speed = message.toInt();
            if(header.equals("LeftMotor"))
            {
              if(speed > 0)
              {
                LeftMotor.SetSpeed(LeftMotor.MaxForward() * (speed / 100.0), ack);
              }
              else 
              {
                LeftMotor.SetSpeed(LeftMotor.MaxReverse() * (speed / 100.0), ack);
              }
            }
            else if(header.equals("RightMotor"))
            {
              if(speed > 0)
              {
                RightMotor.SetSpeed(RightMotor.MaxForward() * (speed / 100.0), ack);
              }
              else 
              {
                RightMotor.SetSpeed(RightMotor.MaxReverse() * (speed / 100.0), ack);
              }
            }
            else if (header.equals("ServoMotor"))
            {
              if(speed > 0)
              {
                ServoMotor.SetSpeed(ServoMotor.MaxForward() * (speed / 100.0), ack);
              }
              else 
              {
                ServoMotor.SetSpeed(ServoMotor.MaxReverse() * (speed / 100.0), ack);
              }
            }
          }
        }
        else
        {
          Serial.write( logger.MakeMessage("No end of message received, could not execute command").c_str() );
        }
      }
      else
      {
        Serial.write( logger.MakeMessage("Unknown address received, could not execute command").c_str() );
      }
    }
    else
    {
      // No one is allowed to use the Serial port other than us, and since we are not at the lower part might as well just send it out
      Serial.write( logger.MakeMessage("Error in last sent packet, no header").c_str() );
    }

    // Clear the string when we are done
    inputString = "";
    stringComplete = false;
  }

  // Check if we have a message to send out
  if(messageBoard.count() > 0)
  {
    // We have at least one message to send out, so let's send out the first one and leave, because we don't want to hold onto the mutex for ever
    
    // Let's hold onto the mutex so that we don't use the messageBoard while someone else else is also trying to use it
    xSemaphoreTake(xSemaphore,0);
   
    // Send the message out
    Serial.write( messageBoard.dequeue().c_str() );

    // Give up the mutex
    xSemaphoreGive(xSemaphore);
  }
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
