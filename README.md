# semubot_bringup

Launch and configuration package for Semubot.

This package contains launch files for starting common runtime tools such as joystick teleop and the micro-ROS agent.

## Current launch files

### joy_teleop.launch.py

Starts joystick input and converts it to `/cmd_vel`.

Launch:

    ros2 launch semubot_bringup joy_teleop.launch.py

This launch file starts:

    joy_node
    teleop_twist_joy_node

Command output:

    /cmd_vel

The joystick node reads the controller using:

    device_id: 0
    deadzone: 0.15
    autorepeat_rate: 20.0

The teleop node loads:

    config/joy_config.yaml

The teleop node publishes:

    geometry_msgs/msg/Twist

with:

    publish_stamped_twist: false

Use this launch file when you want to drive the robot manually with a joystick.

Check output with:

    ros2 topic echo /cmd_vel

If `/cmd_vel` is not published, check:

    joystick is connected
    /joy topic exists
    enable/deadman button is pressed
    config/joy_config.yaml is installed correctly

Useful checks:

    ros2 topic echo /joy
    ros2 topic echo /cmd_vel

### agent.launch.py

Starts the micro-ROS agent for STM32 communication.

Launch with default serial port:

    ros2 launch semubot_bringup agent.launch.py

Default serial port:

    /dev/semubot_wheelbase

Launch with a specific serial port:

    ros2 launch semubot_bringup agent.launch.py serial_port:=/dev/ttyACM0

This launch file runs:

    micro_ros_agent serial --dev <serial_port> -b 115200

Use this launch file when the STM32 firmware uses micro-ROS.

Typical use cases:

    ros2ctrl-microros
    onboard-microros

If the agent repeatedly reconnects, check:

    USB cable
    STM32 reset behavior
    firmware stability
    publishing rate on STM32
    diagnostics load
    correct serial port

## Command convention

Main robot command topic:

    /cmd_vel

Message type:

    geometry_msgs/msg/Twist

Meaning:

    linear.x  = forward/backward
    linear.y  = left/right
    angular.z = rotation/yaw

Example forward command:

    ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

## ros2ctrl_microros.launch.py

Starts the full `ros2ctrl-microros` stack.

Launch:

    ros2 launch semubot_bringup ros2ctrl_microros.launch.py

With a specific STM32 serial port:

    ros2 launch semubot_bringup ros2ctrl_microros.launch.py serial_port:=/dev/ttyACM0

With joystick teleop enabled:

    ros2 launch semubot_bringup ros2ctrl_microros.launch.py use_joy:=true

With joystick and a specific serial port:

    ros2 launch semubot_bringup ros2ctrl_microros.launch.py serial_port:=/dev/ttyACM0 use_joy:=true

This launch file starts:

    micro_ros_agent
    robot_state_publisher
    ros2_control_node
    joint_state_broadcaster
    semubot_velocity_controller
    optional joystick teleop

Default serial port:

    /dev/semubot_wheelbase

Default baud rate:

    115200

The robot description is loaded from:

    semubot_description/urdf/semubot.urdf.xacro

The ros2_control controller config is loaded from:

    semubot_ros_control/config/semubot_controllers.yaml

Expected command flow:

    /cmd_vel
    -> semubot_velocity_controller
    -> ros2_control
    -> semubot_hardware_interface
    -> /hardware_interface/velocity_cmd
    -> STM32 micro-ROS
    -> PWM duty

Encoder feedback flow:

    STM32 encoders
    -> /motor_states
    -> semubot_hardware_interface
    -> ros2_control state interfaces
    -> semubot_velocity_controller

For this stack, PID is done on the ROS 2 controller side.

The STM32 should act as:

    duty receiver + encoder publisher

If the agent prints:

    Serial port not found

check the STM32 device path:

    ls /dev/ttyACM*
    ls /dev/ttyUSB*

Then launch with the correct port:

    ros2 launch semubot_bringup ros2ctrl_microros.launch.py serial_port:=/dev/ttyACM0