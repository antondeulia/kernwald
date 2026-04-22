cmake_minimum_required(VERSION 3.8)
project(kernwald_perception)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)

find_package(OpenCV REQUIRED COMPONENTS highgui imgproc)

add_executable(cube_detector src/cube_detector.cpp)
ament_target_dependencies(cube_detector rclcpp sensor_msgs cv_bridge)
target_link_libraries(cube_detector ${OpenCV_LIBS})

install(TARGETS
  cube_detector
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
