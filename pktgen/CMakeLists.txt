cmake_minimum_required (VERSION 2.8.4)
project (pcap_tutorial)

include_directories(include)

set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -Wextra -Wno-unused-parameter -ggdb -g")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

find_package(PCAP REQUIRED)

message (STATUS "This is CMAKE_CXX_FLAGS " ${CMAKE_CXX_FLAGS})

add_executable (sniffer sniffex.c)
target_link_libraries (sniffer ${PCAP_LIBRARIES})
set_target_properties (sniffer PROPERTIES COMPILE_FLAGS ${CMAKE_CXX_FLAGS})

add_executable (read_pcap packet_parser.c main.c)
target_link_libraries (read_pcap ${PCAP_LIBRARIES})
set_target_properties (read_pcap PROPERTIES COMPILE_FLAGS ${CMAKE_CXX_FLAGS})
