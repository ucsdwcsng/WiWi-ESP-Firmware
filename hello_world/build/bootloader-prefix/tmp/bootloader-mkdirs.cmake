# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/Users/sureel/esp/esp-idf/components/bootloader/subproject"
  "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader"
  "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader-prefix"
  "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader-prefix/tmp"
  "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader-prefix/src/bootloader-stamp"
  "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader-prefix/src"
  "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/Users/sureel/VS_Code/WiWi-ESP-Firmware/hello_world/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
