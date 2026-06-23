import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
import numpy as np

class Processor(Node):
    def __init__(self):
        super().__init__('AutoStop')
        self.sub = self.create_subscription(LaserScan, '/scan', self.callback, 10)
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

    def callback(self, msg):
        all_point = msg.ranges 
        first_point = all_point[0]

        msg_auto_drive = TwistStamped()
        if first_point < 2.0 :
            self.get_logger().info(f"first point : {first_point}")
            msg_auto_drive.twist.linear.x = 0.0
            msg_auto_drive.twist.linear.y = 0.0
            msg_auto_drive.twist.linear.z = 0.0
            msg_auto_drive.twist.angular.z += 0.3
        else :
            msg_auto_drive.twist.linear.x += 0.2

        self.pub.publish(msg_auto_drive)



           

def main():
    rclpy.init()
    node = Processor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
