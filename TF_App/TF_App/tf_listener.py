import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from tf2_geometry_msgs import PointStamped
import tf2_ros
import math
class TFListener(Node):
    def __init__(self):
        super().__init__('tf_listener')

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        # self.timer = self.create_timer(0.5, self.lookup_tf)

    def scan_callback(self, scan: LaserScan):
        self.lookup_tf(scan)

    def lookup_tf(self,msg: LaserScan):
        for i, distance in enumerate(msg.ranges) :
            point = PointStamped()
            # point.header.frame_id = 'hello_base_link'
            point.header.frame_id = 'hello_laser'
            # point.header.frame_id = 'hello_base_link'
            point.header.stamp = rclpy.time.Time()
            angle = msg.angle_min + (i * msg.angle_increment)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            point.point.x = x
            point.point.y = y
            point.point.z = 0

            try:
                # transformed = self.tf_buffer.transform(point, 'hello_laser')
                # transformed = self.tf_buffer.transform(point, 'hello_base_link')
                transformed = self.tf_buffer.transform(point, 'hello_odom')

                self.get_logger().info(
                    f"TF point: i={i}, x={transformed.point.x:.2f}, y={transformed.point.y:.2f}, z={transformed.point.z:.2f}"
                )

            except Exception as e:
                self.get_logger().warn(f"TF not ready: {e}")

def main():
    rclpy.init()
    node = TFListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()