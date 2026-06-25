import math
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from tf_transformations import euler_from_quaternion
from tf2_geometry_msgs import PointStamped
import tf2_ros
import math

# import laspy
import numpy as np

class SimpleYawObstacleAvoider(Node):
    def __init__(self):
        super().__init__('simple_yaw_obstacle_avoider')

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.state = "MOVE"
        self.rotate_cnt=0
        self.front_threshold = 0.25
        self.linear_speed = 0.2
        self.angular_speed = 0.5
        
        self.current_yaw = 0.0
        self.target_yaw = 0.0
        self.yaw_tolerance = 0.05
        self.rotation_angle = math.pi / 6

    def odom_callback(self, msg: Odometry):
        q = msg.pose.pose.orientation
        quat = [q.x, q.y, q.z, q.w]
        _, _, self.current_yaw = euler_from_quaternion(quat)

    def scan_callback(self, scan: LaserScan):
        left_vals = [r for r in scan.ranges[:31] if math.isfinite(r)]
        left_avg = sum(left_vals)/len(left_vals) if left_vals else 0.0

        right_vals = [r for r in scan.ranges[-30:] if math.isfinite(r)]
        right_avg = sum(right_vals)/len(right_vals) if right_vals else 0.0

        front_vals = left_vals + right_vals
        front_min = min(front_vals) if front_vals else float('inf')

        twist = TwistStamped()
        self.get_logger().info(f'self.rotate_cnt: "{self.rotate_cnt}"')
        if self.state == "TURN":
            angle_diff = self.normalize_angle(self.target_yaw - self.current_yaw)

            if abs(angle_diff) > self.yaw_tolerance:
                self.rotate_cnt+=1
                if self.rotate_cnt>10:
                    self.rotate_cnt=0
                    twist.twist.linear.x = -1 * self.linear_speed
                    twist.twist.angular.z = self.angular_speed * (1 if angle_diff > 0 else -1) * 3
                else:
                    twist.twist.linear.x = 0.0
                    twist.twist.angular.z = self.angular_speed * (1 if angle_diff > 0 else -1)

            else:
                # self.rotate_cnt=0
                self.state = "MOVE"

        else:
            if front_min > self.front_threshold:
                twist.twist.linear.x = self.linear_speed
                twist.twist.angular.z = 0.0
                # self.rotate_cnt=0
            else:
                self.state = "TURN"
                self.rotate_cnt+=1
                turn_dir = 1 if left_avg > right_avg else -1
                self.target_yaw = self.normalize_angle(
                    self.current_yaw + turn_dir * self.rotation_angle
                )
                if self.rotate_cnt>10:
                    self.rotate_cnt=0
                    twist.twist.linear.x = -1 * self.linear_speed
                    twist.twist.angular.z = self.angular_speed * turn_dir * 3

                else:
                    twist.twist.linear.x = 0.0
                    twist.twist.angular.z = self.angular_speed * turn_dir

        self.cmd_pub.publish(twist)

        # for i, distance in enumerate(scan.ranges) :
        #     point = PointStamped()
        #     point.header.frame_id = 'base_scan'
        #     point.header.stamp = rclpy.time.Time()
        #     angle = scan.angle_min + (i * scan.angle_increment)
        #     x = distance * math.cos(angle)
        #     y = distance * math.sin(angle)
        #     point.point.x = x
        #     point.point.y = y
        #     point.point.z = 0

        #     try:
        #         transformed = self.tf_buffer.transform(point, 'odom')

        #         self.get_logger().info(
        #             f"TF point: i={i}, x={transformed.point.x:.2f}, y={transformed.point.y:.2f}, z={transformed.point.z:.2f}"
        #         )

        #     except Exception as e:
        #         self.get_logger().warn(f"TF not ready: {e}")

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    # def save_or_append_las(file_path, x_arr, y_arr, z_arr, intensity_arr=None, version="1.2"):
    #     temp_header = laspy.LasHeader(point_format=0, version=version)
    #     temp_las = laspy.LasData(temp_header)

    #     temp_las.x = x_arr
    #     temp_las.y = y_arr
    #     temp_las.z = z_arr
    #     if intensity_arr is not None:
    #         temp_las.intensity = intensity_arr

    #     new_points = temp_las.points

    #     if not os.path.exists(file_path):
    #         with laspy.open(file_path, mode="w", header=temp_header) as writer:
    #             writer.write_points(new_points)
    #     else:
    #         with laspy.open(file_path, mode="a") as appender:
    #             appender.append_points(new_points)


def main():
    rclpy.init()
    node = SimpleYawObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()