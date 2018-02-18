#include "IMU.h"

IMU::IMU()
{
    _Logger = new MessageMaker("IMU","Log");
    _DataStream = new MessageMaker("IMU","Data");

    for(int i = 0; i < 3; i++)
    {
        (_lowpassFilters + i) = new FilterOnePole(LOWPASS, 10000000);
        _checkpoints[i] = 0;
        _sensitivity_thresholds[i] = 0;
    }
    _oldtime = 0; 
    _newtime = 0;
    _MPU9250(0);
}

void IMU::SetMessagingBoard (SemaphoreHandle_t mutex, Queue<String>* messageBoard)
{
  _messageBoard = messageBoard;
  _messageBoardMutex = mutex;
}

bool IMU::Init()
{
    Wire.begin();
    SendMessage(_Logger.MakeMessage("Wire Started"), false);

    // Read the WHO_AM_I register, this is a good test of communication
    byte c = _MPU9250.readByte(_MPU9250.MPU9250_ADDRESS, WHO_AM_I_MPU9250);
    if (c == 0x71) // WHO_AM_I should always be 0x68
    {
        SendMessage(_Logger.MakeMessage("IMU is online"), false);

        // Start by performing self test and reporting values
        _MPU9250.MPU9250SelfTest(_MPU9250.SelfTest);
        SendMessage(_Logger.MakeMessage("IMU has run self tests"), false);

        // Calibrate gyro and accelerometers, load biases in bias registers
        _MPU9250.calibrateMPU9250(_MPU9250.gyroBias, _MPU9250.accelBias);
        SendMessage(_Logger.MakeMessage("IMU has been calibrated"), false);

        // Initialize device for active mode read of accelerometer, gyroscope, and
        // temperature
        _MPU9250.initMPU9250();
        SendMessage(_Logger.MakeMessage("IMU initialized for active data mode"), false);
    } // if (c == 0x71)
    else
    {
        SendMessage(_Logger.MakeMessage("IMU Failed to boot"), false);
        return false;
    }
    return true;
}

void IMU::ReadValues()
{
    // If intPin goes high, all data registers have new data
    // On interrupt, check if data ready interrupt
    if (_MPU9250.readByte(_MPU9250.MPU9250_ADDRESS, INT_STATUS) & 0x01)
    {
        _MPU9250.readGyroData(_MPU9250.gyroCount);  // Read the x/y/z adc values
        _MPU9250.getGres();

        // Calculate the gyro value into actual degrees per second
        // This depends on scale being set
        _MPU9250.gx = (float)_MPU9250.gyroCount[0]*_MPU9250.gRes;
        _MPU9250.gy = (float)_MPU9250.gyroCount[1]*_MPU9250.gRes;
        _MPU9250.gz = (float)_MPU9250.gyroCount[2]*_MPU9250.gRes;

    } // if (readByte(myIMU.MPU9250_ADDRESS, INT_STATUS) & 0x01)
}

void IMU::UpdateCount()
{
    if (!AHRS)
    {
        _MPU9250.delt_t = millis() - _MPU9250.count;
        if (_MPU9250.delt_t > IMU_time)
        {
        _MPU9250.count = millis();
        } // if (myIMU.delt_t > IMU_time)
    } // if (!AHRS)
    else
    {
        // Serial print and/or display at 0.5 s rate independent of data rates
        _MPU9250.delt_t = millis() - _MPU9250.count;

        // update LCD once per half-second independent of read rate
        if (_MPU9250.delt_t > IMU_time)
        {
        _MPU9250.count = millis();
        _MPU9250.sumCount = 0;
        _MPU9250.sum = 0;
        } // if (myIMU.delt_t > IMU_time)
    } // if (AHRS)
}

void IMU::UpdateValues()
{
    if ( millis() > 2000)
    {
        if (millis() < calibtime + 2000)
        { 
            _newtime = millis();
            _checkpoints[0] = _checkpoints[0] + (_MPU9250.gx * (_newtime-_oldtime));
            _checkpoints[1] = _checkpoints[1] + (_MPU9250.gy * (_newtime-_oldtime));
            _checkpoints[2] = _checkpoints[2] + (_MPU9250.gz * (_newtime-_oldtime));
            
            _oldtime = _newtime;

            if (abs(_MPU9250.gx) > _sensitivity_thresholds[0])
                _sensitivity_thresholds[0] = abs(_MPU9250.gx);  
                
            if (abs(_MPU9250.gy) > _sensitivity_thresholds[1])
                _sensitivity_thresholds[1] = abs(_MPU9250.gy);  
                
            if (abs(_MPU9250.gz) > _sensitivity_thresholds[2])
                _sensitivity_thresholds[2] = abs(_MPU9250.gz);    
            }
        else
        {
            _newtime = millis();

            if (abs(_MPU9250.gx) > _sensitivity_thresholds[0]*2)
            {
                _roll = _roll + ((_MPU9250.gx - (_checkpoints[0]/calibtime))*(_newtime-_oldtime))/1000;
                _lowpassFilters[0].input(_roll);
            }
            if (abs(_MPU9250.gy) > _sensitivity_thresholds[1]*2)
            {
                _pitch = _pitch + ((_MPU9250.gy - (_checkpoints[1]/calibtime))*(_newtime-_oldtime))/1000;
                _lowpassFilters[1].input(_pitch);
            }
            if (abs(_MPU9250.gz) > _sensitivity_thresholds[2]*2)
            {
                _yaw = _yaw + ((_MPU9250.gz - (_checkpoints[2]/calibtime))*(_newtime-_oldtime))/1000;
                _lowpassFilters[2].input(_yaw);
            }
            
            ReportValues();
            _oldtime = _newtime;
        }    
    }
}

void IMU::ReadValues()
{
    // Only hold the mutex for one message
    SendMessage(_DataStream.MakeMessage(String(_roll) + ',' + String(_pitch) + ',' +String(_yaw)));
}

void Loop( void * parameter  )
{
    for(;;)
    {
        // Read the register values from the IMU if there are new values
        ReadValues();
    
        // Must be called before updating quaternions!
        _MPU9250.updateTime();

        // Update the internal count of the IMU
        UpdateCount();

        // Update our internal variables and report values if appropriate
        UpdateValues();
    }
}