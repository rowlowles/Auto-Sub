#define configENABLE_BACKWARD_COMPATIBILITY 1 
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


void setup()
{
  // Start the serial communication
  Serial.begin(38400);

  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

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
  IMU _IMU();

  // Allocate the pins for the motors
  LeftMotor.SetPin( 6 );
  RightMotor.SetPin( 5 );
  ServoMotor.SetPin( 3 );

  // Set up the required messaging variables
  LeftMotor.SetMessagingBoard(xSemaphore, &messageBoard);
  RightMotor.SetMessagingBoard(xSemaphore, &messageBoard);
  ServoMotor.SetMessagingBoard(xSemaphore, &messageBoard);
  _IMU.SetMessagingBoard(xSemaphore, &messageBoard);

  // Run the needed initialization for the IMU
  _IMU.Init();

  // Create a thread to monitor the IMU data 
  xTaskCreate(
    _IMU.Loop,        /* Task function. */
    "IMUThread",      /* String with name of task. */
    10000,            /* Stack size in words. */
    NULL,             /* Parameter passed as input of the task */
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

      } 
      else if (header.equals("LeftMotor"))
      {

      }
      else if (header.equals("RightMotor"))
      {

      }
      else if (header.equals("ServoMotor"))
      {

      }
    }
    else
    {
      // No one is allowed to use the Serial port other than us, and since we are not at the lower part might as well just send it out
      Serial.write( _Logger.MakeMessage("Error in last sent packet, no header") );
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
    Serial.write( messageBoard.dequeue() );

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
