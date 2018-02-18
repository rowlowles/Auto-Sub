/* 
    This is the base class for all classes that create messages to be sent over serial
*/
#ifndef SUB_MESSAGE_MAKER
#define SUB_MESSAGE_MAKER

#include <WString.h>

class MessageMaker
{
    public:

    MessageMaker() = delete;

    MessageMaker (String userName, String type)
    {
      _userName = userName;
      _type = type;
    }

    String MakeMessage(String src)
    {
        return ("[" + _type + "] - " + src + "(" + _userName +")\n");
    }

    protected:
    String _userName;
    String _type;
};

#endif // SUB_MESSAGE_MAKER
