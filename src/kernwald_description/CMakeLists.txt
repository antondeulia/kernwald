cmake_minimum_required(VERSION 3.8)
project(kernwald_description)

# This package has no C/C++ targets, but the workspace may enable this globally.
# Touching the variable avoids the "Manually-specified variables were not used"
# warning from CMake for this package.
if(DEFINED CMAKE_EXPORT_COMPILE_COMMANDS)
  set(_kernwald_description_export_compile_commands "${CMAKE_EXPORT_COMPILE_COMMANDS}")
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch rviz2
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
