PROJECT(LenaFace)
cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(lena  lena.cpp)
TARGET_LINK_LIBRARIES(lena ${CONAN_LIBS})

ADD_EXECUTABLE(load-image load-image.cpp)
TARGET_LINK_LIBRARIES(load-image ${CONAN_LIBS})
configure_file(normal.tiff "${CMAKE_BINARY_DIR}/bin" COPYONLY)
configure_file(jbig.tiff "${CMAKE_BINARY_DIR}/bin" COPYONLY)
configure_file(lzma.tiff "${CMAKE_BINARY_DIR}/bin" COPYONLY)
