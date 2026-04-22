#include <rclcpp/rclcpp.hpp>

class CubeDetectorNode : public rclcpp::Node
{
public:
  CubeDetectorNode()
  : Node("cube_detector")
  {
    RCLCPP_INFO(get_logger(), "cube_detector node started");
  }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CubeDetectorNode>());
  rclcpp::shutdown();
  return 0;
}
