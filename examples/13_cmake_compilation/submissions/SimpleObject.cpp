#include "SimpleObject.h"
#include <iostream>
#include <string>

SimpleObject::SimpleObject(std::string name)
{
    myName = name;
}

std::string SimpleObject::getMyName()
{
    return myName;
}

void SimpleObject::sayHello()
{
    std::cout << "Hello! I am a simple object which was created using a .h and .cpp." << std::endl << "These were included in the cmakelists.txt file. My name is " << getMyName() << std::endl;
}