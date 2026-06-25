from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessStart


def generate_launch_description():

    publisher = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--', 'bash', '-c',
            'source ~/colcon_ws/install/setup.bash; '
            'ros2 run test_pkg_4 talker; '
            'exec bash'
        ],
        output='screen'
    )

    processor = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--', 'bash', '-c',
            'source ~/colcon_ws/install/setup.bash; '
            'ros2 run test_pkg_4 processor; '
            'exec bash'
        ],
        output='screen'
    )

    subscriber = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--', 'bash', '-c',
            'source ~/colcon_ws/install/setup.bash; '
            'ros2 run test_pkg_4 listener; '
            'exec bash'
        ],
        output='screen'
    )

    return LaunchDescription([
        publisher,

        RegisterEventHandler(
            OnProcessStart(
                target_action=publisher,
                on_start=[processor]
            )
        ),

        RegisterEventHandler(
            OnProcessStart(
                target_action=processor,
                on_start=[subscriber]
            )
        ),
    ])