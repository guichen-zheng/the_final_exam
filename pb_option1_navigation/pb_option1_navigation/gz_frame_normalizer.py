from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from tf2_ros import TransformBroadcaster


class GzFrameNormalizer(Node):
    def __init__(self) -> None:
        super().__init__('gz_frame_normalizer')

        self.declare_parameter('input_scan_topic', '/scan_raw')
        self.declare_parameter('output_scan_topic', '/scan')
        self.declare_parameter('input_odom_topic', '/odom_raw')
        self.declare_parameter('output_odom_topic', '/odom')
        self.declare_parameter('scan_frame_id', 'front_rplidar_a2')
        self.declare_parameter('odom_frame_id', 'odom')
        self.declare_parameter('base_frame_id', 'base_footprint')

        input_scan_topic = self.get_parameter('input_scan_topic').get_parameter_value().string_value
        output_scan_topic = self.get_parameter('output_scan_topic').get_parameter_value().string_value
        input_odom_topic = self.get_parameter('input_odom_topic').get_parameter_value().string_value
        output_odom_topic = self.get_parameter('output_odom_topic').get_parameter_value().string_value
        self.scan_frame_id = self.get_parameter('scan_frame_id').get_parameter_value().string_value
        self.odom_frame_id = self.get_parameter('odom_frame_id').get_parameter_value().string_value
        self.base_frame_id = self.get_parameter('base_frame_id').get_parameter_value().string_value

        self.scan_pub = self.create_publisher(LaserScan, output_scan_topic, 10)
        self.odom_pub = self.create_publisher(Odometry, output_odom_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(LaserScan, input_scan_topic, self.handle_scan, 10)
        self.create_subscription(Odometry, input_odom_topic, self.handle_odom, 10)

    def handle_scan(self, msg: LaserScan) -> None:
        msg.header.frame_id = self.scan_frame_id
        self.scan_pub.publish(msg)

    def handle_odom(self, msg: Odometry) -> None:
        msg.header.frame_id = self.odom_frame_id
        msg.child_frame_id = self.base_frame_id
        self.odom_pub.publish(msg)
        self.publish_transform(msg)

    def publish_transform(self, msg: Odometry) -> None:
        transform = TransformStamped()
        transform.header.stamp = msg.header.stamp
        transform.header.frame_id = self.odom_frame_id
        transform.child_frame_id = self.base_frame_id
        transform.transform.translation.x = msg.pose.pose.position.x
        transform.transform.translation.y = msg.pose.pose.position.y
        transform.transform.translation.z = msg.pose.pose.position.z
        transform.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(transform)


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
