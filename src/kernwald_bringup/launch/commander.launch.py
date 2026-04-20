from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    target = LaunchConfiguration("target")

    moveit_config = (
        MoveItConfigsBuilder("kernwald", package_name="kernwalt_moveit_config")
        .robot_description()
        .robot_description_semantic()
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .planning_scene_monitor(
            # RViz MotionPlanning needs both URDF and SRDF on topics when RViz
            # is launched outside moveit_rviz.launch.py.
            publish_robot_description=True,
            publish_robot_description_semantic=True,
        )
        .to_moveit_configs()
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict(), {"use_sim_time": True}],
    )

    # commander = Node(
    #     package="kernwald_commander_cpp",
    #     executable="commander",
    #     output="screen",
    #     arguments=[target],
    #     parameters=[moveit_config.to_dict(), {"use_sim_time": True}],
    # )

    return LaunchDescription(
        [
            move_group,
        ]
    )
