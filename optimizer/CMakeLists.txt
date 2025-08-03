cmake_minimum_required(VERSION 3.16)
project(iMOPSE)

set(CMAKE_CXX_STANDARD 17)

file(GLOB_RECURSE SOURCES "src/*.h" "src/*.cpp")

include_directories(src)
add_executable(imopse ${SOURCES} "src/factories/method/methods/SO/GPHH/CGPHHFactory.cpp" "src/factories/method/methods/SO/GPHH/CGPHHFactory.h" "src/method/methods/SO/GPHH/CGPHH.cpp" "src/method/methods/SO/GPHH/CGPHH.h")
