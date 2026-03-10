#!/usr/bin/env python3
"""
物体跟随节点（优化版）
功能: 根据物体中心位置和距离实现平滑跟随
- 物体偏离中心 → 转向
- 物体远 → 前进；近 → 停止或后退
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point, Twist


class FollowBehaviorNode(Node):
    def __init__(self):
        super().__init__('follow_behavior_node')
        
        # 参数（可通过 launch 或 yaml 调）
        self.declare_parameter('linear_speed_max', 0.5)      # 最大前进速度
        self.declare_parameter('angular_speed_max', 1.0)     # 最大转向速度
        self.declare_parameter('image_width', 640)
        self.declare_parameter('center_tolerance', 60)       # 中心死区像素
        self.declare_parameter('stop_distance', 0.4)         # 太近停止（米）
        self.declare_parameter('approach_distance', 1.0)     # 目标跟随距离（米）
        self.declare_parameter('timeout_sec', 1.0)           # 丢失超时
        
        self.linear_max = self.get_parameter('linear_speed_max').value
        self.angular_max = self.get_parameter('angular_speed_max').value
        self.image_width = self.get_parameter('image_width').value
        self.center_tol = self.get_parameter('center_tolerance').value
        self.stop_dist = self.get_parameter('stop_distance').value
        self.approach_dist = self.get_parameter('approach_distance').value
        self.timeout = self.get_parameter('timeout_sec').value
        
        # 状态
        self.current_object = None
        self.object_position = None   # Point (x: depth, y: horizontal offset)
        self.last_update = self.get_clock().now()
        
        # 订阅
        self.object_sub = self.create_subscription(
            String, '/vision/detected_object', self.object_callback, 10)
        self.position_sub = self.create_subscription(
            Point, '/vision/object_position', self.position_callback, 10)
        
        # 发布
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 控制循环
        self.create_timer(0.05, self.control_loop)   # 20Hz
        
        self.get_logger().info('跟随节点已启动（优化版）')
        
    def object_callback(self, msg):
        self.current_object = msg.data.strip().lower()
        self.last_update = self.get_clock().now()
        
    def position_callback(self, msg):
        self.object_position = msg
        self.last_update = self.get_clock().now()
        
    def control_loop(self):
        twist = Twist()
        
        # 超时检查
        if (self.get_clock().now() - self.last_update).nanoseconds / 1e9 > self.timeout:
            self.stop_robot()
            self.get_logger().info('物体丢失超时，停止', throttle_duration_sec=2.0)
            return
        
        if not self.current_object or not self.object_position:
            self.stop_robot()
            return
        
        # 物体中心偏移（像素）
        image_center = self.image_width / 2.0
        error_x = self.object_position.y - image_center   # y 是水平偏移（注意坐标系）
        error_dist = self.object_position.x               # x 是深度（距离）
        
        # 转向控制（死区 + 比例）
        if abs(error_x) > self.center_tol:
            turn_ratio = error_x / image_center
            twist.angular.z = -self.angular_max * turn_ratio
            twist.angular.z = max(min(twist.angular.z, self.angular_max), -self.angular_max)
        else:
            twist.angular.z = 0.0
        
        # 线速度控制（距离比例）
        dist_error = error_dist - self.approach_dist
        if error_dist > self.stop_dist + 0.1:
            twist.linear.x = self.linear_max * min(1.0, max(0.0, dist_error / 1.0))
        elif error_dist < self.stop_dist - 0.1:
            twist.linear.x = -self.linear_max * 0.3   # 轻微后退
        else:
            twist.linear.x = 0.0
        
        # 发布
        self.cmd_vel_pub.publish(twist)
        
    def stop_robot(self):
        twist = Twist()
        self.cmd_vel_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = FollowBehaviorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()