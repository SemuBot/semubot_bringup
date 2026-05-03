from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    serial_port = LaunchConfiguration("serial_port")
    baud_rate = LaunchConfiguration("baud_rate")
    use_joy = LaunchConfiguration("use_joy")

    robot_description_file = LaunchConfiguration("robot_description_file")
    controllers_file = LaunchConfiguration("controllers_file")

    robot_description = {
        "robot_description": Command([
            "xacro ",
            robot_description_file,
        ])
    }

    agent_node = Node(
        package="micro_ros_agent",
        executable="micro_ros_agent",
        name="micro_ros_agent",
        arguments=[
            "serial",
            "--dev", serial_port,
            "-b", baud_rate,
            "-v0",
        ],
        output="screen",
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[
            robot_description,
        ],
        output="screen",
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            controllers_file,
        ],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    semubot_velocity_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "semubot_velocity_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    joy_teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("semubot_bringup"),
                "launch",
                "joy_teleop.launch.py",
            ])
        ]),
        condition=IfCondition(use_joy),
    )
    return LaunchDescription([
        DeclareLaunchArgument(
            "serial_port",
            default_value="/dev/semubot_wheelbase",
            description="Serial port for STM32 micro-ROS agent",
        ),

        DeclareLaunchArgument(
            "baud_rate",
            default_value="115200",
            description="Baud rate for micro-ROS serial transport",
        ),

        DeclareLaunchArgument(
            "use_joy",
            default_value="false",
            description="Start joystick teleop",
        ),

        DeclareLaunchArgument(
            "robot_description_file",
            default_value=PathJoinSubstitution([
                FindPackageShare("semubot_description"),
                "urdf",
                "semubot.urdf.xacro",
            ]),
            description="Path to Semubot URDF/Xacro file",
        ),

        DeclareLaunchArgument(
            "controllers_file",
            default_value=PathJoinSubstitution([
                FindPackageShare("semubot_ros_control"),
                "config",
                "semubot_controllers.yaml",
            ]),
            description="Path to ros2_control controllers YAML file",
        ),

        agent_node,
        robot_state_publisher_node,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        semubot_velocity_controller_spawner,
        joy_teleop_launch,
    ])