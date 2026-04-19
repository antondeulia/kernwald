from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    bringup_pkg = FindPackageShare("kernwald_bringup")
    description_pkg = FindPackageShare("kernwald_description")
    moveit_config_pkg = FindPackageShare("kernwalt_moveit_config")

    controllers_config = PathJoinSubstitution(
        [bringup_pkg, "config", "ros2_controllers.yaml"]
    )
    rviz2_config = PathJoinSubstitution([bringup_pkg, "rviz2", "config.rviz"])

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

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[controllers_config],
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )

    gripper_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller"],
    )

    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_config_pkg, "launch", "move_group.launch.py"])
        )
    )

    rviz2 = Node(package="rviz2", executable="rviz2", arguments=["-d", rviz2_config])

    return LaunchDescription(
        [
            robot_state_publisher,
            controller_manager,
            joint_state_broadcaster,
            arm_controller,
            gripper_controller,
            move_group,
            rviz2,
        ]
    )
