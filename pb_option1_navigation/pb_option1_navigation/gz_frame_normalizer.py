import math

from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage


class GzFrameNormalizer(Node):
    def __init__(self) -> None:
        super().__init__('gz_frame_normalizer')

        self.declare_parameter('input_scan_topic', '/scan_raw')
        self.declare_parameter('output_scan_topic', '/scan')
        self.declare_parameter('input_odom_topic', '/odom_raw')
        self.declare_parameter('output_odom_topic', '/odom')
        self.declare_parameter('input_tf_topic', '/tf_raw')
        self.declare_parameter('output_tf_topic', '/tf')
        self.declare_parameter('scan_frame_id', 'front_rplidar_a2')
        self.declare_parameter('scan_min_valid_range', 0.45)
        self.declare_parameter('odom_frame_id', 'odom')
        self.declare_parameter('base_frame_id', 'base_footprint')

        input_scan_topic = self.get_parameter('input_scan_topic').get_parameter_value().string_value
        output_scan_topic = self.get_parameter('output_scan_topic').get_parameter_value().string_value
        input_odom_topic = self.get_parameter('input_odom_topic').get_parameter_value().string_value
        output_odom_topic = self.get_parameter('output_odom_topic').get_parameter_value().string_value
        input_tf_topic = self.get_parameter('input_tf_topic').get_parameter_value().string_value
        output_tf_topic = self.get_parameter('output_tf_topic').get_parameter_value().string_value
        self.scan_frame_id = self.get_parameter('scan_frame_id').get_parameter_value().string_value
        self.scan_min_valid_range = (
            self.get_parameter('scan_min_valid_range').get_parameter_value().double_value
        )
        self.odom_frame_id = self.get_parameter('odom_frame_id').get_parameter_value().string_value
        self.base_frame_id = self.get_parameter('base_frame_id').get_parameter_value().string_value

        self.scan_pub = self.create_publisher(LaserScan, output_scan_topic, 10)
        self.odom_pub = self.create_publisher(Odometry, output_odom_topic, 10)
        self.tf_pub = self.create_publisher(TFMessage, output_tf_topic, 10)

        self.create_subscription(LaserScan, input_scan_topic, self.handle_scan, 10)
        self.create_subscription(Odometry, input_odom_topic, self.handle_odom, 10)
        self.create_subscription(TFMessage, input_tf_topic, self.handle_tf, 10)

    @staticmethod
    def _leaf_frame_id(frame_id: str) -> str:
        parts = [part for part in frame_id.split('/') if part]
        if not parts:
            return frame_id
        return parts[-1]

    def handle_scan(self, msg: LaserScan) -> None:
        msg.header.frame_id = self.scan_frame_id
        msg.range_min = max(msg.range_min, float(self.scan_min_valid_range))
        msg.ranges = [
            math.inf if math.isfinite(scan_range) and scan_range < self.scan_min_valid_range else scan_range
            for scan_range in msg.ranges
        ]
        self.scan_pub.publish(msg)

    def handle_odom(self, msg: Odometry) -> None:
        msg.header.frame_id = self.odom_frame_id
        msg.child_frame_id = self.base_frame_id
        self.odom_pub.publish(msg)

    def handle_tf(self, msg: TFMessage) -> None:
        normalized_transforms = []
        for transform in msg.transforms:
            parent_frame = self._leaf_frame_id(transform.header.frame_id)
            child_frame = self._leaf_frame_id(transform.child_frame_id)

            if parent_frame != self.odom_frame_id or child_frame != self.base_frame_id:
                continue

            transform.header.frame_id = self.odom_frame_id
            transform.child_frame_id = self.base_frame_id
            normalized_transforms.append(transform)

        if normalized_transforms:
            self.tf_pub.publish(TFMessage(transforms=normalized_transforms))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GzFrameNormalizer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
