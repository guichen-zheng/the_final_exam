#!/usr/bin/env python3
"""
命令解释节点
功能: 物体 → 动作映射
- 水杯(cup) → 直行(forward)
- 苹果(apple) → 左转(turn left)
- 香蕉(banana) → 右转(turn right)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class CommandInterpreterNode(Node):
    def __init__(self):
        super().__init__('command_interpreter_node')
        
        # 物体→动作映射
        self.action_map = {
            'cup': {'linear': 0.3, 'angular': 0.0, 'desc': '直行'},
            'apple': {'linear': 0.0, 'angular': 3.0, 'desc': '左转'},
            'banana': {'linear': 0.0, 'angular': -3.0, 'desc': '右转'}
        }
        
        self.current_object = None
        self.last_detection = self.get_clock().now()
        
        # 订阅检测结果
        self.object_sub = self.create_subscription(
            String, '/vision/detected_object', self.object_callback, 10)
        
        # 发布速度命令
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 控制定时器
        self.create_timer(0.1, self.execute_action)
        
        self.get_logger().info('命令解释节点已启动')
        self.get_logger().info('映射: 水杯→直行, 苹果→左转, 香蕉→右转')
        
    def object_callback(self, msg):
        detected = msg.data
        if detected != self.current_object:
            self.current_object = detected
            action = self.action_map.get(detected, {})
            desc = action.get('desc', '未知')
            self.get_logger().info(f'检测到 {detected} → 执行 {desc}')
        self.last_detection = self.get_clock().now()
        
    def execute_action(self):
        # 超时停止
        if (self.get_clock().now() - self.last_detection).nanoseconds / 1e9 > 5.0:
            if self.current_object:
                self.current_object = None
                self.get_logger().info('超时停止', throttle_duration_sec=2.0)
            self.cmd_vel_pub.publish(Twist())
            return
        
        # 执行动作
        if self.current_object and self.current_object in self.action_map:
            action = self.action_map[self.current_object]
            twist = Twist()
            twist.linear.x = action['linear']
            twist.angular.z = action['angular']
            self.cmd_vel_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = CommandInterpreterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
