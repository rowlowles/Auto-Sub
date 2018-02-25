/* 
    This is the base class for all classes that create messages to be sent over serial
*/
#ifndef SUB_MESSAGE_MAKER
#define SUB_MESSAGE_MAKER

#include <WString.h>

class MessageMaker
{
    public:

    MessageMaker();

    MessageMaker (String userName, String type)
    {
      _userName = userName;
      _type = type;
    }

    String MakeMessage(String src)
    {
        return ( String("[") + _type + String("]") + src + String("(") + _userName + String(")\n") );
    }
    
    String _userName;
    String _type;
};

#endif // SUB_MESSAGE_MAKER

