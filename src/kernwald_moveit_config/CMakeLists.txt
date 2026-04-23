cmake_minimum_required(VERSION 3.22)
project(kernwald_moveit_config)

# This package has no C/C++ targets, but the workspace may enable this globally.
# Touching the variable avoids the "Manually-specified variables were not used"
# warning from CMake for this package.
if(DEFINED CMAKE_EXPORT_COMPILE_COMMANDS)
  set(_kernwald_moveit_config_export_compile_commands "${CMAKE_EXPORT_COMPILE_COMMANDS}")
endif()

find_package(ament_cmake REQUIRED)

ament_package()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/launch")
  install(
    DIRECTORY launch
    DESTINATION share/${PROJECT_NAME}
    PATTERN "setup_assistant.launch" EXCLUDE)
endif()

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})
