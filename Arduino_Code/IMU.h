/* 
The purpose of this class is to provide a wrapper for common IMU functions and to enable the use of common serial communication methods 
*/

#ifndef _SUB_IMU_H
#define _SUB_IMU_H

// External Libraries
#include "MPU9250.h"
#include "Filters.h"

// Standard Libraries
#include "Wire.h"

// Custom Libraries
#include "Constants.h"
#include "SubMutex.h"

#define  AHRS  true         // Set to false for basic data read
#define  SerialDebug  false  // Set to true to get Serial output for debugging
#define IMU_time 50
#define calibtime 5000.0

class IMU {

    public: 
    
    IMU();

    // This method does all the required initialization tasks for the IMU, it is important to note that this method will return false if the IMU was not initialized correctly 
    bool Init ();

    // This method wraps the methods for sending a message to the message board, the function accepts the message that is to be sent
    void SendMessage (bool data);

    // This method gives the class a method of posting messages to the message board
    void SetMessagingBoard (SubMutex* mutex);

    void updateIMU ();

    private:
    // Internal functions to help with value updating
    void ReadValues();
    void UpdateCount();
    void UpdateValues();
    void ReportValues();

    // Variables to control message passing
    SubMutex* _messageBoardMutex;
    String _message;

    // Variables to control IMU data collection and filtering
    double _oldtime;
    double _newtime;

    double _roll;
    double _pitch;
    double _yaw;

    double _checkpoints[3];
    double _sensitivity_thresholds [3];

    MPU9250* _MPU9250; 
    FilterOnePole _lowpassFilters [3];
};

#endif

