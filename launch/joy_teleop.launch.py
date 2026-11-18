import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def check_profile(context, profile_file):
    path = profile_file.perform(context)
    if not os.path.isfile(path):
        raise RuntimeError(f'Profile not found: {path}')


def generate_launch_description():
    profile_file = PathJoinSubstitution([
        FindPackageShare('semubot_config'),
        'profiles',
        [LaunchConfiguration('profile'), '.yaml'],
    ])

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
        name='teleop_twist_joy_node',
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
        joy_node,
        teleop_node,
    ])
