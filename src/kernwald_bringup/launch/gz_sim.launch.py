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
        MoveItConfigsBuilder("kernwald", package_name="kernwald_moveit_config")
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
            publish_planning_scene=True,
            publish_geometry_updates=True,
            publish_state_updates=True,
            publish_transforms_updates=True,
        )
        .sensors_3d(file_path="config/sensors_3d.yaml")
        .to_moveit_configs()
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        parameters=[
            moveit_config.to_dict(),
            {
                "use_sim_time": True,
                # Keep a stable world frame for OctoMap integration from depth points.
                "octomap_frame": "base_footprint",
                "octomap_resolution": 0.03,
            },
        ],
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
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
    )

    sensor_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/rgbd_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/rgbd_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/rgbd_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        remappings=[
            ("/rgbd_camera/depth_image", "/depth_camera"),
            ("/rgbd_camera/camera_info", "/depth_camera/camera_info"),
            ("/rgbd_camera/points", "/depth_camera/points"),
            ("/rgbd_camera/image", "/rgb_camera"),
        ],
        parameters=[
            {
                "override_frame_id": "depth_camera_link",
                # Avoid PointCloud2 backlog and long latency in MoveIt/RViz.
                "qos_overrides./depth_camera/camera_info.publisher.reliability": "best_effort",
                "qos_overrides./depth_camera/camera_info.publisher.history": "keep_last",
                "qos_overrides./depth_camera/camera_info.publisher.depth": 1,
                "qos_overrides./depth_camera/points.publisher.reliability": "best_effort",
                "qos_overrides./depth_camera/points.publisher.history": "keep_last",
                "qos_overrides./depth_camera/points.publisher.depth": 1,
            }
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
            clock_bridge,
            sensor_bridge,
            kernwald_spawner,
            joint_state_broadcaster,
            arm_controller,
            gripper_controller,
            rviz2,
            move_group,
        ]
    )
