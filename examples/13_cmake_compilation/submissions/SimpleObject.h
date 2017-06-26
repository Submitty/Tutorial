// in myclass.h
#include <string>
class SimpleObject
{
    public:
        SimpleObject(std::string name);
        std::string getMyName();
        void sayHello();
    private:
        std::string myName;
};