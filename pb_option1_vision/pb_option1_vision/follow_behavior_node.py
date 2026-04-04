#!/usr/bin/env python3
"""
物体跟随节点（方向已翻转版 - 适配内置摄像头镜像）
- 已确认可以左右转，现在整体颠倒转向方向
- x小（≈30）→ 实际右边 → 现在应左转
- x大（≈300）→ 实际左边 → 现在应右转
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point, Twist


class FollowBehaviorNode(Node):
    def __init__(self):
        super().__init__('follow_behavior_node')
        
        # 参数
        self.declare_parameter('linear_speed_max', 0.5)
        self.declare_parameter('angular_speed_max', 1.0)
        self.declare_parameter('image_width', 640)
        self.declare_parameter('center_point', 165.0)      # 镜像后的中心点
        self.declare_parameter('center_tolerance', 50)
        self.declare_parameter('stop_distance', 0.4)
        self.declare_parameter('approach_distance', 1.0)
        self.declare_parameter('timeout_sec', 1.0)
        
        self.linear_max = self.get_parameter('linear_speed_max').value
        self.angular_max = self.get_parameter('angular_speed_max').value
        self.image_width = self.get_parameter('image_width').value
        self.center_point = self.get_parameter('center_point').value
        self.center_tol = self.get_parameter('center_tolerance').value
        self.stop_dist = self.get_parameter('stop_distance').value
        self.approach_dist = self.get_parameter('approach_distance').value
        self.timeout = self.get_parameter('timeout_sec').value
        
        self.current_object = None
        self.object_position = None
        self.last_update = self.get_clock().now()
        
        self.object_sub = self.create_subscription(
            String, '/vision/detected_object', self.object_callback, 10)
        self.position_sub = self.create_subscription(
            Point, '/vision/object_position', self.position_callback, 10)
        
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.create_timer(0.05, self.control_loop)
        
        self.get_logger().info(f'跟随节点已启动（方向已翻转版 - 中心点 {self.center_point:.1f}）')

    def object_callback(self, msg):
        self.current_object = msg.data.strip().lower()
        self.last_update = self.get_clock().now()

    def position_callback(self, msg):
        self.object_position = msg
        self.last_update = self.get_clock().now()

    def control_loop(self):
        twist = Twist()

        if (self.get_clock().now() - self.last_update).nanoseconds / 1e9 > self.timeout:
            self.stop_robot()
            self.get_logger().info('物体丢失超时，停止', throttle_duration_sec=2.0)
            return

        if not self.current_object or not self.object_position:
            self.stop_robot()
            return

        # ========== 方向已翻转的核心逻辑 ==========
        x = self.object_position.x
        error_x = x - self.center_point
        
        if abs(error_x) > self.center_tol:
            turn_ratio = error_x / (self.image_width / 4.0)
            # 关键修改：把 + 改成 - ，整体颠倒转向方向
            twist.angular.z = -self.angular_max * turn_ratio
            twist.angular.z = max(min(twist.angular.z, self.angular_max), -self.angular_max)
            
            side = "右边（应左转）" if error_x > 0 else "左边（应右转）"
            self.get_logger().info(
                f'物体在画面{side} | x: {x:.1f} | error: {error_x:+.1f} | 转向: {twist.angular.z:+.2f} rad/s',
                throttle_duration_sec=0.5
            )
        else:
            twist.angular.z = 0.0
            self.get_logger().info(f'物体接近居中 | x: {x:.1f} | 不转向', throttle_duration_sec=1.0)
        # ===========================================

        # 距离控制（使用 y 作为深度）
        error_dist = self.object_position.y - self.approach_dist
        if self.object_position.y > self.stop_dist + 0.1:
            twist.linear.x = self.linear_max * min(1.0, max(0.0, error_dist / 1.0))
        elif self.object_position.y < self.stop_dist - 0.1:
            twist.linear.x = -self.linear_max * 0.3
        else:
            twist.linear.x = 0.0

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