#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <thread>

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("test_moveit");

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);

    std::thread spin_thread([&executor]()
                            { executor.spin(); });

    std::cout << "Hello my friend" << std::endl;

    // Arm
    auto arm = moveit::planning_interface::MoveGroupInterface(node, "arm");
    arm.setMaxVelocityScalingFactor(1.0);
    arm.setMaxAccelerationScalingFactor(1.0);

    auto gripper = moveit::planning_interface::MoveGroupInterface(node, "gripper");

    // // Named goal
    // arm.setStartStateToCurrentState();
    // arm.setNamedTarget("pose_1");

    // moveit::planning_interface::MoveGroupInterface::Plan plan1;
    // bool success = (arm.plan(plan1)) == moveit::core::MoveItErrorCode::SUCCESS;

    // if (success)
    // {
    //     arm.execute(plan1);
    // }

    // // Home
    // arm.setStartStateToCurrentState();
    // arm.setNamedTarget("home");

    // moveit::planning_interface::MoveGroupInterface::Plan plan2;
    // bool success2 = (arm.plan(plan2)) == moveit::core::MoveItErrorCode::SUCCESS;

    // if (success2)
    // {
    //     arm.execute(plan2);
    // }

    // ------------------------------------------------

    // Joint goal
    // std::vector<double> joints = {1.5, 0.5, 0.0, 1.5, 0.0, -0.7};

    // arm.setStartStateToCurrentState();
    // arm.setJointValueTarget(joints);

    // moveit::planning_interface::MoveGroupInterface::Plan plan1;

    // bool success = (arm.plan(plan1)) == moveit::core::MoveItErrorCode::SUCCESS;

    // if (success)
    // {
    //     arm.execute(plan1);
    // }

    // ---------------------------------------------------
    // Pose goal

    tf2::Quaternion q;
    q.setRPY(3.14, 0.0, 0.0);
    q = q.normalize();

    geometry_msgs::msg::PoseStamped target_pose;
    target_pose.header.frame_id = "base_link";
    target_pose.pose.position.x = 0.0;
    target_pose.pose.position.y = -0.7;
    target_pose.pose.position.x = 0.4;

    target_pose.pose.orientation.x = q.getX();
    target_pose.pose.orientation.y = q.getY();
    target_pose.pose.orientation.z = q.getZ();
    target_pose.pose.orientation.w = q.getW();

    arm.setStartStateToCurrentState();
    arm.setPoseTarget(target_pose);

    moveit::planning_interface::MoveGroupInterface::Plan plan1;
    bool success = (arm.plan(plan1)) == moveit::core::MoveItErrorCode::SUCCESS;
    if (success)
    {
        arm.execute(plan1);
    }

    // Cartesian path

    std::vector<geometry_msgs::msg::Pose> waypoints;
    geometry_msgs::msg::Pose pose1 = arm.getCurrentPose().pose;
    pose1.position.z += -0.2;
    waypoints.push_back(pose1);

    moveit_msgs::msg::RobotTrajectory trajectory;

    double fraction = arm.computeCartesianPath(waypoints, 0.01, trajectory);

    if (fraction == 1)
    {
        arm.execute(trajectory);
    }

    rclcpp::shutdown();
    spin_thread.join();
    return 0;
}