#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

using ImageMsg = sensor_msgs::msg::Image;

class CubeDetection : public rclcpp::Node
{
public:
    CubeDetection() : Node("cube_detection")
    {
        depth_img_sub_ = this->create_subscription<ImageMsg>(
            "/depth_camera",
            10,
            std::bind(&CubeDetection::depth_img_callback, this, std::placeholders::_1)
        );
    }

private:
    void depth_img_callback(const ImageMsg::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "Received an image: %d/%d", msg->height, msg->width);
    }

    rclcpp::Subscription<ImageMsg>::SharedPtr depth_img_sub_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<CubeDetection>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}