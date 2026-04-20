#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <tf2/LinearMath/Quaternion.h>

#include <thread>

using MoveGroupInterface = moveit::planning_interface::MoveGroupInterface;

struct TargetPose
{
    double x;
    double y;
    double z;
    double roll;
    double pitch;
    double yaw;
};

class Commander
{
public:
    Commander(std::shared_ptr<rclcpp::Node> node)
    {
        node_ = node;

        arm_ = std::make_shared<MoveGroupInterface>(node_, "arm");
        arm_->startStateMonitor();
        arm_->setMaxVelocityScalingFactor(1.0);
        arm_->setMaxAccelerationScalingFactor(1.0);

        gripper_ = std::make_shared<MoveGroupInterface>(node_, "gripper");

        pre_grasp_ = {0.7, 0.0, 0.4, 3.14, 0.0, 0.0};
        place_ = {0.20, 0.20, 0.20, 0.0, 3.14, 0.0};
    }

    void goToPoseTarget(const TargetPose &targetPose)
    {
        const auto &[x, y, z, roll, pitch, yaw] = targetPose;

        tf2::Quaternion q;
        q.setRPY(roll, pitch, yaw);
        q.normalize();

        geometry_msgs::msg::PoseStamped target_pose;
        target_pose.header.frame_id = "base_link";
        target_pose.pose.position.x = x;
        target_pose.pose.position.y = y;
        target_pose.pose.position.z = z;

        target_pose.pose.orientation.x = q.getX();
        target_pose.pose.orientation.y = q.getY();
        target_pose.pose.orientation.z = q.getZ();
        target_pose.pose.orientation.w = q.getW();

        arm_->setStartStateToCurrentState();
        arm_->setPoseTarget(target_pose);
        planAndExecute(arm_);
    }

    void moveArmToNamedTarget(const std::string &target_name)
    {
        arm_->setStartStateToCurrentState();
        arm_->setNamedTarget(target_name);
        planAndExecute(arm_);
    }

    // Gripper
    void openGripper()
    {
        gripper_->setStartStateToCurrentState();
        gripper_->setNamedTarget("open");
        planAndExecute(gripper_);
    }

    void closeGripper()
    {
        gripper_->setStartStateToCurrentState();
        gripper_->setNamedTarget("closed");
        planAndExecute(gripper_);
    }

private:
    void planAndExecute(
        const std::shared_ptr<MoveGroupInterface> &interface)
    {
        MoveGroupInterface::Plan plan;

        const auto plan_result = interface->plan(plan);
        if (plan_result != moveit::core::MoveItErrorCode::SUCCESS)
        {
            return;
        }

        const auto execute_result = interface->execute(plan);
        if (execute_result != moveit::core::MoveItErrorCode::SUCCESS)
        {
            return;
        }
    }

    std::shared_ptr<rclcpp::Node> node_;
    std::shared_ptr<MoveGroupInterface> arm_;
    std::shared_ptr<MoveGroupInterface> gripper_;

    TargetPose pre_grasp_;
    TargetPose place_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>(
        "commander",
        rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread executor_thread([&executor]()
                                { executor.spin(); });

    auto commander = Commander(node);
    const auto target_name = argc > 1 ? std::string(argv[1]) : std::string("pose_1");

    commander.moveArmToNamedTarget(target_name);
    commander.closeGripper();
    commander.openGripper();

    executor.cancel();
    if (executor_thread.joinable())
    {
        executor_thread.join();
    }
    rclcpp::shutdown();
    return 0;
}
