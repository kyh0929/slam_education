import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray

import numpy as np

class Processor(Node):
    def __init__(self):
        super().__init__('processor')
        self.sub = self.create_subscription(String, '/direction', self.callback, 10)
        self.pub = self.create_publisher(Int32MultiArray, '/direction_process', 10)
        self.position = np.array([0,0])

    def callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')
        length = len(msg.data.encode('utf-8'))
        for c in msg.data:
            if c=="w" :
                self.tmp = np.array([0,1])
                self.position = self.position + self.tmp    
            elif c=="s" :
                self.tmp = np.array([0,-1])
                self.position = self.position + self.tmp    
            elif c=='d' :
                self.tmp = np.array([1,0])
                self.position = self.position + self.tmp    
            elif c=='a' :
                self.tmp = np.array([-1,0])
                self.position = self.position + self.tmp    

        print(self.position)
        msg_numpy = Int32MultiArray()
        msg_numpy.data = self.position.flatten().tolist()
        self.pub.publish(msg_numpy)
def main():
    rclpy.init()
    node = Processor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
