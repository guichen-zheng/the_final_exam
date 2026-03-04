#!/usr/bin/env python3
"""
命令解释节点 - 精确1秒动作模式（Twist版，稳定可靠）
每次检测到物体就动作1秒，然后自动停止
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class CommandInterpreterNode(Node):
    def __init__(self):
        super().__init__('command_interpreter_node')
        
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 当前动作定时器（1秒后停止）
        self.action_timer = None
        self.current_twist = Twist()
        
        # 订阅检测结果
        self.object_sub = self.create_subscription(
            String, '/vision/detected_object', self.object_callback, 10)
        
        self.get_logger().info('命令解释节点已启动 (精确1秒动作模式)')
        self.get_logger().info('cup → 直行1秒 | apple → 左转1秒 | banana → 右转1秒')
        
    def object_callback(self, msg):
        detected = msg.data.strip().lower()
        
        # 先停止上一次动作
        if self.action_timer:
            self.action_timer.cancel()
        
        twist = Twist()
        
        if detected == 'cup':
            twist.linear.x = 0.6      # 直行速度（可调）
            desc = '直行1秒'
        elif detected == 'apple':
            twist.angular.z = 1.2     # 左转速度（可调）
            desc = '左转1秒'
        elif detected == 'banana':
            twist.angular.z = -1.2    # 右转速度（可调）
            desc = '右转1秒'
        else:
            return
        
        self.current_twist = twist
        self.cmd_vel_pub.publish(twist)
        
        self.get_logger().info(f'检测到 {detected} → {desc}')
        
        # 1秒后自动停止
        self.action_timer = self.create_timer(1.0, self.stop_action)
        
    def stop_action(self):
        """1秒后停止"""
        stop_twist = Twist()
        self.cmd_vel_pub.publish(stop_twist)
        self.action_timer = None


def main(args=None):
    rclpy.init(args=args)
    node = CommandInterpreterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()