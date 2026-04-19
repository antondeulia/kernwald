#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>

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

    void moveToPreGrasp()
    {
        goToPoseTarget(pre_grasp_);
    }

private:
    void planAndExecute(const std::shared_ptr<MoveGroupInterface> &interface)
    {
        MoveGroupInterface::Plan plan;
        bool success = (interface->plan(plan)) == moveit::core::MoveItErrorCode::SUCCESS;
        if (success)
        {
            interface->execute(plan);
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

    auto node = std::make_shared<rclcpp::Node>("commander");
    auto commander = Commander(node);

    commander.moveToPreGrasp();

    rclcpp::shutdown();
    return 0;
}