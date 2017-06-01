//The following is a very simple program for use with the cmake compilation example.
//It simply prints one line, creates an instance of the SimpleObject Class, and then
//invokes the sayHello method of that class.
#include <iostream>
#include "SimpleObject.h"
int main()
{
    std::cout << "Hello world. This was compiled using cmake." << std::endl;
    SimpleObject simple("Jan");
    simple.sayHello();
    return 0;
}