from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    description_pkg = FindPackageShare("kernwald_description")

    rviz2_config = PathJoinSubstitution([description_pkg, "rviz2", "config.rviz"])

    robot_description = Command(
        [
            "xacro",
            " ",
            PathJoinSubstitution([description_pkg, "urdf", "kernwald.xacro"]),
        ]
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui", executable="joint_state_publisher_gui"
    )

    rviz2 = Node(package="rviz2", executable="rviz2", arguments=["-d", rviz2_config])

    return LaunchDescription([robot_state_publisher, joint_state_publisher_gui, rviz2])
