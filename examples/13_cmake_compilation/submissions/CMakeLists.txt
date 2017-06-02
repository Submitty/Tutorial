cmake_minimum_required (VERSION 2.8)
project (cmakeTest)

#name this project's executable.
set(my_executable a.out)

# toggle for building a 32 bit version (for Dr. Memory)
set(BUILD_32 "")
#set(BUILD_32 " -m32 ")

# all the .cpp and .h files that make up this project
add_executable(${my_executable}
  main.cpp
  SimpleObject.cpp
  SimpleObject.h
)
