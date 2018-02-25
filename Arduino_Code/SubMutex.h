#ifndef _SUB_MUTEX_H
#define _SUB_MUTEX_H

#include <Arduino.h>

class SubMutex
{
    public : 

    SubMutex()
    {
      state = 0;
    }

    void TakeMutex()
    {
      while(state) 
      {
        // We don't want to over run things
        delay(10); 
      }
      // Update the state to be taken
      state = 1;
    }

    void GiveMutex()
    {
      state = 0; 
    }

    private:

    volatile int state;

};

#endif

