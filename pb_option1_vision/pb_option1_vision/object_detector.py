#!/usr/bin/env python3
"""
YOLO物体检测节点
功能: 检测水杯、苹果、香蕉
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO


class ObjectDetectorNode(Node):
    def __init__(self):
        super().__init__('object_detector_node')
        
        # 参数
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('device', 'cpu')
        
        model_path = self.get_parameter('model_path').value
        self.conf_threshold = self.get_parameter('confidence_threshold').value
        device = self.get_parameter('device').value
        
        # 初始化YOLO
        self.get_logger().info(f'加载YOLO模型: {model_path}')
        self.model = YOLO(model_path)
        self.model.to(device)
        
        # CV Bridge
        self.bridge = CvBridge()
        
        # 目标类别 (COCO dataset)
        self.target_classes = {
            'cup': 41,      # 水杯
            'apple': 47,    # 苹果
            'banana': 46    # 香蕉
        }
        
        # 订阅图像
        self.image_sub = self.create_subscription(
            Image,
            '/image',
            self.image_callback,
            10
        )
        
        # 发布检测结果
        self.object_pub = self.create_publisher(String, '/vision/detected_object', 10)
        self.position_pub = self.create_publisher(Point, '/vision/object_position', 10)
        self.image_pub = self.create_publisher(Image, '/vision/annotated_image', 10)
        
        self.get_logger().info('物体检测节点已启动')
        self.get_logger().info('目标类别: cup(水杯), apple(苹果), banana(香蕉)')
        
    def image_callback(self, msg):
        try:
            # 转换图像
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            
            # YOLO检测
            results = self.model(cv_image, conf=self.conf_threshold, verbose=False)[0]
            
            # 处理检测结果
            detected_object = None
            max_confidence = 0.0
            object_center = Point()
            
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # 检查是否是目标类别
                for obj_name, target_id in self.target_classes.items():
                    if class_id == target_id and confidence > max_confidence:
                        max_confidence = confidence
                        detected_object = obj_name
                        
                        # 计算中心点
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        object_center.x = (x1 + x2) / 2.0
                        object_center.y = (y1 + y2) / 2.0
                        object_center.z = float(confidence)
            
            # 发布结果
            if detected_object:
                object_msg = String()
                object_msg.data = detected_object
                self.object_pub.publish(object_msg)
                self.position_pub.publish(object_center)
                
                self.get_logger().info(
                    f'检测到: {detected_object} (置信度: {max_confidence:.2f})',
                    throttle_duration_sec=1.0
                )
            
            # 发布标注图像
            annotated = results.plot()
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated, 'bgr8')
            annotated_msg.header = msg.header
            self.image_pub.publish(annotated_msg)
            
        except Exception as e:
            self.get_logger().error(f'检测错误: {str(e)}')


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
