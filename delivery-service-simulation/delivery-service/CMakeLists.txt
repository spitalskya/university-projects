cmake_minimum_required(VERSION 3.6.2)

set(TARGET_NAME deliveryService)
project(${TARGET_NAME})

set(CMAKE_CXX_STANDARD 23)

set(SOURCE_FILES
        DeliveryService.cpp
        Map.cpp
        City.cpp
        CityHasher.cpp
        CourierHandler.cpp
        Courier.cpp
        Package.cpp
)

set(TEST_FILES
        testDeliveryService.cpp
        testMap.cpp
        testCity.cpp
        testCourier.cpp
        testCourierHandler.cpp
        testPackage.cpp
        )

set(GTEST_SOURCE_FILES
        GoogleTest/gtest-death-test.cc
        GoogleTest/gtest-filepath.cc
        GoogleTest/gtest-port.cc
        GoogleTest/gtest-printers.cc
        GoogleTest/gtest-test-part.cc
        GoogleTest/gtest-typed-test.cc
        GoogleTest/gtest.cc
        GoogleTest/gtest_main.cc)

add_library(tests OBJECT ${TEST_FILES})
add_library(gtest OBJECT ${GTEST_SOURCE_FILES})

find_package(Threads REQUIRED)

include_directories(GoogleTest)
add_executable(${TARGET_NAME} ${SOURCE_FILES} ${TEST_FILES} ${GTEST_SOURCE_FILES})
target_link_libraries(${TARGET_NAME} ${CMAKE_THREAD_LIBS_INIT})

add_custom_command(TARGET deliveryService PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/files/small_map.txt
        ${CMAKE_SOURCE_DIR}/files/dijkstra_test_map.txt
        ${CMAKE_SOURCE_DIR}/files/slovak_map.txt
        ${CMAKE_SOURCE_DIR}/files/bad_map_file.txt
        $<TARGET_FILE_DIR:deliveryService>
        VERBATIM)
