#include "IMU.h"

#define IMU_LOOPS 10

IMU::IMU()
{
    _oldtime = 0; 
    _newtime = 0;
    _MPU9250 = new MPU9250();
    _message.reserve(25);
    counter = 0;
    _sendTime = 0; 
    _sendRate = 45.0; // Hz

    _rollFilter = FilterOnePole( LOWPASS, 1000);
    _pitchFilter = FilterOnePole( LOWPASS, 1000);
    _yawFilter = FilterOnePole( LOWPASS, 1000);
}

bool IMU::Init()
{
    Wire.begin();
    _message = "Wire Started";
    SendMessage(false);

    // Read the WHO_AM_I register, this is a good test of communication
    byte c = _MPU9250->readByte(0x68, WHO_AM_I_MPU9250);
    if (c == 0x71) // WHO_AM_I should always be 0x68
    {
        _message = "Online";
        SendMessage(false);

        // Start by performing self test and reporting values
        _MPU9250->MPU9250SelfTest(_MPU9250->SelfTest);
        _message = "Run self tests";
        SendMessage(false);

        // Calibrate gyro and accelerometers, load biases in bias registers
        _MPU9250->calibrateMPU9250(_MPU9250->gyroBias, _MPU9250->accelBias);
        _message = "Calibrated";
        SendMessage(false);

        // Initialize device for active mode read of accelerometer, gyroscope, and
        // temperature
        _MPU9250->initMPU9250();
        _message = "Initialized";
        SendMessage(false);

        // Get magnetometer calibration from AK8963 ROM
        _MPU9250->initAK8963(_MPU9250->magCalibration);
        _message = "Mag Ready";
        SendMessage(false);
    } // if (c == 0x71)
    else
    {
        _message = "Failed to boot";
        SendMessage(false);
        return false;
    }
    return true;
}

void IMU::ReadValues()
{
 // If intPin goes high, all data registers have new data
  // On interrupt, check if data ready interrupt
  if (_MPU9250->readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)
  {  
    // Read the x/y/z adc values
    _MPU9250->readAccelData(_MPU9250->accelCount);  
    _MPU9250->getAres();

    // Now we'll calculate the accleration value into actual g's
    // This depends on scale being set
    _MPU9250->ax = (float)_MPU9250->accelCount[0]*_MPU9250->aRes; // - accelBias[0];
    _MPU9250->ay = (float)_MPU9250->accelCount[1]*_MPU9250->aRes; // - accelBias[1];
    _MPU9250->az = (float)_MPU9250->accelCount[2]*_MPU9250->aRes; // - accelBias[2];

    // Read the x/y/z adc values
    _MPU9250->readGyroData(_MPU9250->gyroCount);  
    _MPU9250->getGres();

    // Calculate the gyro value into actual degrees per second
    // This depends on scale being set
    _MPU9250->gx = (float)_MPU9250->gyroCount[0]*_MPU9250->gRes;
    _MPU9250->gy = (float)_MPU9250->gyroCount[1]*_MPU9250->gRes;
    _MPU9250->gz = (float)_MPU9250->gyroCount[2]*_MPU9250->gRes;

    // Read the x/y/z adc values
    _MPU9250->readMagData(_MPU9250->magCount);  
    _MPU9250->getMres();
    // User environmental x-axis correction in milliGauss, should be
    // automatically calculated
    _MPU9250->magbias[0] = +470.;
    // User environmental x-axis correction in milliGauss TODO axis??
    _MPU9250->magbias[1] = +120.;
    // User environmental x-axis correction in milliGauss
    _MPU9250->magbias[2] = +125.;

    // Calculate the magnetometer values in milliGauss
    // Include factory calibration per data sheet and user environmental
    // corrections
    // Get actual magnetometer value, this depends on scale being set
    _MPU9250->mx = (float)_MPU9250->magCount[0]*_MPU9250->mRes*_MPU9250->magCalibration[0] -
               _MPU9250->magbias[0];
    _MPU9250->my = (float)_MPU9250->magCount[1]*_MPU9250->mRes*_MPU9250->magCalibration[1] -
               _MPU9250->magbias[1];
    _MPU9250->mz = (float)_MPU9250->magCount[2]*_MPU9250->mRes*_MPU9250->magCalibration[2] -
               _MPU9250->magbias[2];
  } // if (readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)

  // Must be called before updating quaternions!
  _MPU9250->updateTime();

  // Sensors x (y)-axis of the accelerometer is aligned with the y (x)-axis of
  // the magnetometer; the magnetometer z-axis (+ down) is opposite to z-axis
  // (+ up) of accelerometer and gyro! We have to make some allowance for this
  // orientationmismatch in feeding the output to the quaternion filter. For the
  // MPU-9250, we have chosen a magnetic rotation that keeps the sensor forward
  // along the x-axis just like in the LSM9DS0 sensor. This rotation can be
  // modified to allow any convenient orientation convention. This is ok by
  // aircraft orientation standards! Pass gyro rate as rad/s
//  MadgwickQuaternionUpdate(ax, ay, az, gx*PI/180.0f, gy*PI/180.0f, gz*PI/180.0f,  my,  mx, mz);
  MahonyQuaternionUpdate(_MPU9250->ax, _MPU9250->ay, _MPU9250->az, _MPU9250->gx*DEG_TO_RAD,
                         _MPU9250->gy*DEG_TO_RAD, _MPU9250->gz*DEG_TO_RAD, _MPU9250->my,
                         _MPU9250->mx, _MPU9250->mz, _MPU9250->deltat);
}

void IMU::UpdateValues()
{
    if (!AHRS)
    {
        _MPU9250->delt_t = millis() - _MPU9250->count;
        if (_MPU9250->delt_t > IMU_time)
        {
        _MPU9250->count = millis();
        } // if (_MPU9250->delt_t > IMU_time)
    } // if (!AHRS)
    else
    {
        // Serial print and/or display at 0.5 s rate independent of data rates
        _MPU9250->delt_t = millis() - _MPU9250->count;

        // update LCD once per half-second independent of read rate
        if (_MPU9250->delt_t > IMU_time)
        {
          // Define output variables from updated quaternion---these are Tait-Bryan
          // angles, commonly used in aircraft orientation. In this coordinate system,
          // the positive z-axis is down toward Earth. Yaw is the angle between Sensor
          // x-axis and Earth magnetic North (or true North if corrected for local
          // declination, looking down on the sensor positive yaw is counterclockwise.
          // Pitch is angle between sensor x-axis and Earth ground plane, toward the
          // Earth is positive, up toward the sky is negative. Roll is angle between
          // sensor y-axis and Earth ground plane, y-axis up is positive roll. These
          // arise from the definition of the homogeneous rotation matrix constructed
          // from quaternions. Tait-Bryan angles as well as Euler angles are
          // non-commutative; that is, the get the correct orientation the rotations
          // must be applied in the correct order which for this configuration is yaw,
          // pitch, and then roll.
          // For more see
          // http://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
          // which has additional links.
          _MPU9250->yaw   = atan2(2.0f * (*(getQ()+1) * *(getQ()+2) + *getQ() *
                        *(getQ()+3)), *getQ() * *getQ() + *(getQ()+1) * *(getQ()+1)
                        - *(getQ()+2) * *(getQ()+2) - *(getQ()+3) * *(getQ()+3));
          _MPU9250->pitch = -asin(2.0f * (*(getQ()+1) * *(getQ()+3) - *getQ() *
                        *(getQ()+2)));
          _MPU9250->roll  = atan2(2.0f * (*getQ() * *(getQ()+1) + *(getQ()+2) *
                        *(getQ()+3)), *getQ() * *getQ() - *(getQ()+1) * *(getQ()+1)
                        - *(getQ()+2) * *(getQ()+2) + *(getQ()+3) * *(getQ()+3));
          _MPU9250->pitch *= RAD_TO_DEG;
          _MPU9250->yaw   *= RAD_TO_DEG;
          // Declination of PAC (43.472215° N 80.546244° W) is
          // 9.62° W  ± 0.38°  changing by  0.00° E per year
          // - http://www.ngdc.noaa.gov/geomag-web/#declination
          _MPU9250->yaw   -= 9.62;
          _MPU9250->roll  *= RAD_TO_DEG;

           _MPU9250->roll = _rollFilter.input(_MPU9250->roll);
           _MPU9250->pitch = _pitchFilter.input(_MPU9250->pitch);
           _MPU9250->yaw = _yawFilter.input(_MPU9250->yaw) + 180.0;
          
          _MPU9250->count = millis();
          _MPU9250->sumCount = 0;
          _MPU9250->sum = 0;
        } // if (_MPU9250->delt_t > IMU_time)
    } // if (AHRS)
}

void IMU::ReportValues()
{
    _message = String(_MPU9250->roll) + ',' + String(_MPU9250->pitch) + ',' + String(_MPU9250->yaw);
    SendMessage(true);
}

void IMU::updateIMU()
{
    // Read the register values from the IMU if there are new values
    ReadValues();

    // Update the internal count of the IMU
    UpdateValues();

    if((millis() - _sendTime) > 1000.0/_sendRate)
    {
      _sendTime = millis();
       // Report our values
      ReportValues(); 
    }
}

void IMU::SendMessage (bool data)
{ 
   if(data)
      Serial.print("[Data]");
    else
      Serial.print("[Log]");
    Serial.print(_message);
    Serial.print("(IMU)\n");
}


