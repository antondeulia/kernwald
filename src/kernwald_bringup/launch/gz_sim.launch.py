from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    bringup_pkg = FindPackageShare("kernwald_bringup")
    description_pkg = FindPackageShare("kernwald_description")
    ros_gz_pkg = FindPackageShare("ros_gz_sim")

    world = PathJoinSubstitution([bringup_pkg, "worlds", "world.sdf"])

    robot_description = Command(
        [
            "xacro",
            " ",
            PathJoinSubstitution([description_pkg, "urdf", "kernwald.xacro"]),
            " ",
            "use_gazebo:=true",
            " ",
        ]
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
    )

    # Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([ros_gz_pkg, "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={"gz_args": ["-r ", world]}.items(),
    )

    # ros_gz_bridges
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    # Robot spawner
    kernwald_spawner = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "robot_description"],
        parameters=[{"use_sim_time": True}],
    )

    # Controllers
    controllers = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "arm_controller",
            "gripper_controller",
        ],
    )

    return LaunchDescription(
        [
            robot_state_publisher,
            gz_sim,
            bridge,
            kernwald_spawner,
            controllers,
        ]
    )
