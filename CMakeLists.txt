
# The following lines of boilerplate have to be in your project's CMakeLists
# in this exact order for cmake to work correctlycmake_minimum_required(VERSION 3.5)
cmake_minimum_required(VERSION 3.5)
add_compile_options(-fdiagnostics-color=always)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)

message("EXTRA_COMPONENT_DIRS: " ${EXTRA_COMPONENT_DIRS})

# string(REGEX REPLACE ".*/\(.*\)" "\\1" CURDIR ${CMAKE_CURRENT_SOURCE_DIR})
project(${CMAKE_CURRENT_SOURCE_DIR})

git_describe(PROJECT_VERSION ${COMPONENT_DIR})
message("Project commit: " ${PROJECT_VERSION})

# add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/csi_send)
# add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/csi_recv)
set(PROJECT1_DIR ${CMAKE_CURRENT_SOURCE_DIR}/csi_send)
set(PROJECT1_BUILD_DIR ${CMAKE_BINARY_DIR}/csi_send)
file(MAKE_DIRECTORY ${PROJECT1_BUILD_DIR})
execute_process(COMMAND idf.py -B ${PROJECT1_BUILD_DIR} -D ${PROJECT1_DIR} flash
                WORKING_DIRECTORY ${PROJECT1_BUILD_DIR})

# Build and flash project2
set(PROJECT2_DIR ${CMAKE_CURRENT_SOURCE_DIR}/csi_recv)
set(PROJECT2_BUILD_DIR ${CMAKE_BINARY_DIR}/csi_recv)
file(MAKE_DIRECTORY ${PROJECT2_BUILD_DIR})
execute_process(COMMAND idf.py -B ${PROJECT2_BUILD_DIR} -D ${PROJECT2_DIR} flash
                WORKING_DIRECTORY ${PROJECT2_BUILD_DIR})