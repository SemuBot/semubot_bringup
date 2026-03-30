from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/semubot_wheelbase',
        description='Serial port for micro-ROS agent'
    )

    agent_node = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        arguments=['serial', '--dev', LaunchConfiguration('serial_port'), "-b", "115200", "-v6"],
        output='screen'
    )

    return LaunchDescription([
        serial_port_arg,
        agent_node,
    ])