cmake_minimum_required(VERSION 3.8)
project(kernwald_perception)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

add_executable(cube_detection src/cube_detection.cpp)
ament_target_dependencies(cube_detection rclcpp sensor_msgs)

install(TARGETS
  cube_detection
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
