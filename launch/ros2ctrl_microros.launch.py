import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def check_profile(context, profile_file):
    path = profile_file.perform(context)
    if not os.path.isfile(path):
        raise RuntimeError(f'Profile not found: {path}')


def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port')
    baud_rate = LaunchConfiguration('baud_rate')

    robot_description_file = LaunchConfiguration('robot_description_file')
    profile_file = PathJoinSubstitution([
        FindPackageShare('semubot_config'),
        'profiles',
        [LaunchConfiguration('profile'), '.yaml'],
    ])

    robot_description = {
        'robot_description': ParameterValue(
            Command(['xacro ', robot_description_file]),
            value_type=str,
        )
    }

    agent_node = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        arguments=[
            'serial',
            '--dev', serial_port,
            '-b', baud_rate,
            '-v0',
        ],
        output='screen',
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            robot_description,
        ],
        output='screen',
    )

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            robot_description,
            profile_file,
        ],
        output='screen',
        remappings=[
            ('/semubot_velocity_controller/cmd_vel', '/cmd_vel'),
            ('/semubot_velocity_controller/odom', '/odom'),
            ('/diagnostics', '/controller_manager/diagnostics'),
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager',
        ],
        output='screen',
    )

    semubot_velocity_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'semubot_velocity_controller',
            '--controller-manager',
            '/controller_manager',
        ],
        output='screen',
    )

    motor_fault_diagnostics_node = Node(
        package='semubot_ros_control',
        executable='motor_fault_diagnostics.py',
        output='screen',
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        parameters=[profile_file],
        output='screen',
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        parameters=[profile_file],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'profile',
            default_value=EnvironmentVariable('SEMUBOT_PROFILE', default_value='v2'),
            description='Parameter profile from semubot_config/profiles',
        ),
        OpaqueFunction(function=check_profile, args=[profile_file]),

        DeclareLaunchArgument(
            'serial_port',
            default_value=EnvironmentVariable('SEMUBOT_WHEELBASE_PORT', default_value='/dev/semubot_wheelbase'),
            description='Serial port for STM32 micro-ROS agent',
        ),

        DeclareLaunchArgument(
            'baud_rate',
            default_value='115200',
            description='Baud rate for micro-ROS serial transport',
        ),

        DeclareLaunchArgument(
            'robot_description_file',
            default_value=PathJoinSubstitution([
                FindPackageShare('semubot_description'),
                'urdf',
                'semubot_v2.urdf.xacro',
            ]),
            description='Path to Semubot URDF/Xacro file',
        ),

        agent_node,
        robot_state_publisher_node,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        semubot_velocity_controller_spawner,
        motor_fault_diagnostics_node,
        joy_node,
        teleop_node,
    ])
