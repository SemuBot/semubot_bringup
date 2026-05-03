from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    joy_config = PathJoinSubstitution([
        FindPackageShare('semubot_bringup'),
        'config',
        'joy_config.yaml',
    ])

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        parameters=[
            {
                'device_id': 0,
                'deadzone': 0.15,
                'autorepeat_rate': 20.0,
            }
        ],
        output='screen',
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[
            joy_config,
            {'publish_stamped_twist': False},
        ],
        output='screen',
    )

    return LaunchDescription([
        joy_node,
        teleop_node,
    ])