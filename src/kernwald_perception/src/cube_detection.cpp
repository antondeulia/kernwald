#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>

using ImageMsg = sensor_msgs::msg::Image;
using CameraInfoMsg = sensor_msgs::msg::CameraInfo;

class CubeDetection : public rclcpp::Node
{
public:
    CubeDetection() : Node("cube_detection")
    {
        const auto sensor_qos = rclcpp::SensorDataQoS();

        depth_img_sub_ = this->create_subscription<ImageMsg>(
            "/depth_camera",
            sensor_qos,
            std::bind(&CubeDetection::depth_img_callback, this, std::placeholders::_1)
        );
        rgb_img_sub_ = this->create_subscription<ImageMsg>(
            "/rgb_camera",
            sensor_qos,
            std::bind(&CubeDetection::rgb_img_callback, this, std::placeholders::_1)
        );
        camera_info_sub_ = this->create_subscription<CameraInfoMsg>(
            "/depth_camera/camera_info",
            sensor_qos,
            std::bind(&CubeDetection::camera_info_callback, this, std::placeholders::_1)
        );

        RCLCPP_INFO(this->get_logger(), "Subscribed: /rgb_camera, /depth_camera, /depth_camera/camera_info");
    }

private:
    void depth_img_callback(const ImageMsg::SharedPtr msg)
    {
        // RCLCPP_INFO_THROTTLE(
        //     this->get_logger(),
        //     *this->get_clock(),
        //     2000,
        //     "Depth image: %ux%u, encoding=%s, frame_id=%s",
        //     msg->width,
        //     msg->height,
        //     msg->encoding.c_str(),
        //     msg->header.frame_id.c_str()
        // );
    }

    void rgb_img_callback(const ImageMsg::SharedPtr msg)
    {
        // RCLCPP_INFO_THROTTLE(
        //     this->get_logger(),
        //     *this->get_clock(),
        //     2000,
        //     "RGB image: %ux%u, encoding=%s, frame_id=%s",
        //     msg->width,
        //     msg->height,
        //     msg->encoding.c_str(),
        //     msg->header.frame_id.c_str()
        // );
    }

    void camera_info_callback(const CameraInfoMsg::SharedPtr msg)
    {
        const double fx = msg->k[0];
        const double fy = msg->k[4];
        const double cx = msg->k[2];
        const double cy = msg->k[5];

        RCLCPP_INFO_THROTTLE(
            this->get_logger(),
            *this->get_clock(),
            2000,
            "CameraInfo: %ux%u, fx=%.3f, fy=%.3f, cx=%.3f, cy=%.3f, frame_id=%s",
            msg->width,
            msg->height,
            fx, fy, cx, cy,
            msg->header.frame_id.c_str()
        );
    }

    rclcpp::Subscription<ImageMsg>::SharedPtr depth_img_sub_;
    rclcpp::Subscription<ImageMsg>::SharedPtr rgb_img_sub_;
    rclcpp::Subscription<CameraInfoMsg>::SharedPtr camera_info_sub_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<CubeDetection>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
