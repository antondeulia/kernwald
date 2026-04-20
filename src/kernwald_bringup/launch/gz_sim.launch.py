from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    use_gazebo = LaunchConfiguration("use_gazebo")
    declare_use_gazebo = DeclareLaunchArgument(
        "use_gazebo",
        default_value="true",
        description="Enable Gazebo ros2_control plugin in robot_description.",
    )

    bringup_pkg = FindPackageShare("kernwald_bringup")
    description_pkg = FindPackageShare("kernwald_description")
    ros_gz_pkg = FindPackageShare("ros_gz_sim")

    rviz2_config = PathJoinSubstitution([bringup_pkg, "rviz2", "config.rviz"])
    world = PathJoinSubstitution([bringup_pkg, "worlds", "world.sdf"])

    robot_description = Command(
        [
            "xacro",
            " ",
            PathJoinSubstitution([description_pkg, "urdf", "kernwald.xacro"]),
            " ",
            "use_gazebo:=",
            use_gazebo,
            " ",
        ]
    )

    moveit_config = (
        MoveItConfigsBuilder("kernwald", package_name="kernwalt_moveit_config")
        .robot_description(mappings={"use_gazebo": use_gazebo})
        .robot_description_semantic()
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .planning_scene_monitor(
            # RViz MotionPlanning needs both URDF and SRDF on topics when RViz
            # is launched outside moveit_rviz.launch.py.
            publish_robot_description=False,
            publish_robot_description_semantic=True,
        )
        .to_moveit_configs()
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        parameters=[moveit_config.to_dict(), {"use_sim_time": True}],
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
        launch_arguments={
            "gz_args": [
                "-r ",
                world,
            ]
        }.items(),
    )

    # ros_gz_bridges
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
    )

    # Robot spawner
    kernwald_spawner = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "robot_description"],
        parameters=[{"use_sim_time": True}],
    )

    # Controllers
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

    rviz2 = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz2_config],
        parameters=[
            {"robot_description": robot_description},
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription(
        [
            declare_use_gazebo,
            robot_state_publisher,
            gz_sim,
            bridge,
            kernwald_spawner,
            joint_state_broadcaster,
            arm_controller,
            gripper_controller,
            rviz2,
            move_group,
        ]
    )
