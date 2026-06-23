import rclpy
from rclpy.node import Node
from custom_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('srv_server')

        self.srv = self.create_service(AddTwoInts, '/add_two_ints', self.srv_callback)
        self.get_logger().info('Srv Server Ready.')

    def srv_callback(self, request, response):
        num1 = request.a.num
        num2 = request.b.num
        while num2!=0 :
            num1, num2 = num2, num1%num2

        
        response.sum.num = num1
        
        self.get_logger().info(f'Incoming request\na: {request.a.num}, b: {request.b.num}')
        self.get_logger().info(f'Sending back response: [{response.sum.num}]')
        
        return response


def main():
    rclpy.init()
    node = AddTwoIntsServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
