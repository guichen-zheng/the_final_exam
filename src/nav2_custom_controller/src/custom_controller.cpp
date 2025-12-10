#include "nav2_custom_controller/custom_controller.hpp"
#include "nav2_core/exceptions.hpp"
#include "nav2_util/geometry_utils.hpp"
#include "nav2_util/node_utils.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

namespace nav2_custom_controller {
void CustomController::configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent, std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) {
  node_ = parent.lock();  //从虚指针WeakPtr获取生命周期节点parent.lock()的共享指针node_ 
  costmap_ros_ = costmap_ros;    //直接存储代价地图costmap指针
  tf_ = tf;  //存储坐标变换指针tf
  plugin_name_ = name; 

  // 声明并获取参数，设置最大线速度（默认0.1）和最大角速度（默认1.0）
  nav2_util::declare_parameter_if_not_declared(
      node_, plugin_name_ + ".max_linear_speed", rclcpp::ParameterValue(0.1));
  node_->get_parameter(plugin_name_ + ".max_linear_speed", max_linear_speed_);
  nav2_util::declare_parameter_if_not_declared(
      node_, plugin_name_ + ".max_angular_speed", rclcpp::ParameterValue(1.0));
  node_->get_parameter(plugin_name_ + ".max_angular_speed", max_angular_speed_);
}

void CustomController::cleanup() {
  RCLCPP_INFO(node_->get_logger(),
              "清理控制器：%s 类型为 nav2_custom_controller::CustomController",
              plugin_name_.c_str());
}

void CustomController::activate() {
  RCLCPP_INFO(node_->get_logger(),
              "激活控制器：%s 类型为 nav2_custom_controller::CustomController",
              plugin_name_.c_str());
}

void CustomController::deactivate() {
  RCLCPP_INFO(node_->get_logger(),
              "停用控制器：%s 类型为 nav2_custom_controller::CustomController",
              plugin_name_.c_str());
}

geometry_msgs::msg::TwistStamped CustomController::computeVelocityCommands(  //1.计算速度命令
    const geometry_msgs::msg::PoseStamped &pose,
    const geometry_msgs::msg::Twist &, nav2_core::GoalChecker *) {

  geometry_msgs::msg::TwistStamped cmd_vel;  //定义速度命令  
  return cmd_vel;  //返回速度命令
}

void CustomController::setSpeedLimit(const double &speed_limit,
                                     const bool &percentage) {
  (void)percentage;
  (void)speed_limit;  //没有使用速度限制函数所以(void)了
}

void CustomController::setPlan(const nav_msgs::msg::Path &path) {
  global_plan_ = path;  //setPlan函数把path赋值global_plan_，然后保存到全局变量
}

geometry_msgs::msg::PoseStamped CustomController::getNearestTargetPose(  //2.获取最近目标点
    const geometry_msgs::msg::PoseStamped &current_pose) {

  return current_pose;  //返回当前位置
}

double CustomController::calculateAngleDifference(   //3.获取角度差
    const geometry_msgs::msg::PoseStamped &current_pose,
    const geometry_msgs::msg::PoseStamped &target_pose) {

  return 0.0f;//角度差返回0
}
} // namespace nav2_custom_controller

#include "pluginlib/class_list_macros.hpp"  //这个头文件里有专门用来 “注册插件” 的宏
PLUGINLIB_EXPORT_CLASS(nav2_custom_controller::CustomController,nav2_core::Controller)  
//nav2_custom_controller 命名空间里的 CustomController 这个类作为 nav2_core::Controller （基类）的插件导出