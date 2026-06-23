import sys
import rclpy
from rclpy.node import Node
from custom_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('srv_client')
        self.cli = self.create_client(AddTwoInts, '/add_two_ints')
        
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
            
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a.num = int(a)
        self.req.b.num = int(b)
        
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main():
    rclpy.init()
    client = AddTwoIntsClient()
    response = client.send_request(sys.argv[1], sys.argv[2])
    client.get_logger().info(f'Sum: {response.sum.num}')
    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
