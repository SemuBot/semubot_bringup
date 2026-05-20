# semubot_bringup

> Launch and configuration package for the SemuBot omnidirectional wheelbase.

![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

`semubot_bringup` provides launch files for bringing up the SemuBot stack. Depending on the use case, individual components (joystick, micro-ROS agent) can be started separately, or the full `ros2ctrl-microros` stack can be launched in one command.

---

## Quick Start

```bash
# Full stack with joystick
ros2 launch semubot_bringup ros2ctrl_microros.launch.py

# Full stack, specific serial port
ros2 launch semubot_bringup ros2ctrl_microros.launch.py serial_port:=/dev/ttyACM0 
```

---

## Launch Files

### `ros2ctrl_microros.launch.py` — Full stack

Starts the complete `ros2ctrl-microros` runtime: micro-ROS agent, `ros2_control` node, state broadcaster, and velocity controller.

```bash
ros2 launch semubot_bringup ros2ctrl_microros.launch.py [serial_port:=<port>] 
```

**Arguments**

| Argument | Default | Description |
|---|---|---|
| `serial_port` | `/dev/semubot_wheelbase` | STM32 serial device |

**Nodes started**

| Node | Description |
|---|---|
| `micro_ros_agent` | Bridges micro-ROS on STM32 to ROS 2 |
| `robot_state_publisher` | Publishes TF from URDF |
| `ros2_control_node` | Runs the hardware interface and controllers |
| `joint_state_broadcaster` | Broadcasts joint states |
| `semubot_velocity_controller` | Converts `/cmd_vel` to motor commands |
| `teleop_twist_joy_node` *(optional)* | Converts joystick to `/cmd_vel` |

**Config files loaded**

| File | Purpose |
|---|---|
| `semubot_description/urdf/semubot.urdf.xacro` | Robot description |
| `semubot_ros_control/config/semubot_controllers.yaml` | Controller parameters |
| `config/joy_config.yaml` | Joystick button mapping |

**Data flow**

```
/cmd_vel
    → semubot_velocity_controller
    → ros2_control
    → SemuBotHardwareInterface
    → /hardware_interface/velocity_cmd  [M1, M2, M3] — PWM duty
    → STM32 micro-ROS → motors

STM32 encoders
    → /motor_states
    → SemuBotHardwareInterface
    → ros2_control state interfaces
    → semubot_velocity_controller
```

---

### `joy_teleop.launch.py` — Joystick teleop only

Starts joystick input and converts it to `/cmd_vel`. Use this when controlling the robot manually without launching the full stack.

```bash
ros2 launch semubot_bringup joy_teleop.launch.py
```

**Nodes started:** `joy_node`, `teleop_twist_joy_node`

**Key parameters**

| Parameter | Value |
|---|---|
| `device_id` | `0` |
| `deadzone` | `0.15` |
| `autorepeat_rate` | `20.0` Hz |
| `publish_stamped_twist` | `false` |

**Verify output**

```bash
ros2 topic echo /cmd_vel
```

**Troubleshooting**

| Symptom | Check |
|---|---|
| `/cmd_vel` not published | Joystick connected? `/joy` topic active? |
| No `/joy` topic | Run `ros2 topic echo /joy` — is `joy_node` alive? |
| Robot doesn't move | Enable/deadman button held? |
| Config not applied | Is `config/joy_config.yaml` installed? Run `colcon build` |

---

### `agent.launch.py` — micro-ROS agent only

Starts the micro-ROS agent for STM32 communication. Use this when running a stack that requires the agent as a standalone component.

```bash
# Default port
ros2 launch semubot_bringup agent.launch.py

# Specific port
ros2 launch semubot_bringup agent.launch.py serial_port:=/dev/ttyACM0
```

Runs: `micro_ros_agent serial --dev <serial_port> -b 115200`


**Troubleshooting**

| Symptom | Check |
|---|---|
| `Serial port not found` | `ls /dev/ttyACM*` or `ls /dev/ttyUSB*` — use the correct port |
| Agent repeatedly reconnects | USB cable, STM32 reset behavior, firmware stability, publishing rate, diagnostics load |

---

## Command Convention

| Topic | Type | Description |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | High-level velocity command |
| `/hardware_interface/velocity_cmd` | `std_msgs/Float32MultiArray` | Per-motor PWM duty `[M1, M2, M3]` |
| `/motor_states` | `std_msgs/Float32MultiArray` | Per-motor encoder feedback |

**`/cmd_vel` field mapping**

| Field | Meaning |
|---|---|
| `linear.x` | Forward / backward |
| `linear.y` | Left / right (strafe) |
| `angular.z` | Yaw / rotation |

**Example — forward at 0.1 m/s**

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.10, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

---

## Related Packages

| Package | Description |
|---|---|
| [`semubot_ros_control`](https://github.com/SemuBot/semubot_ros_control) | Hardware interface and velocity controller |
| [`semubot_description`](https://github.com/SemuBot/semubot_description) | URDF and mesh assets |
| [`SemuBot-Firmware`](https://github.com/SemuBot/semubot-firmware/tree/fw/ros2ctrl-microros) | STM32 firmware (FreeRTOS, micro-ROS, DRV8353) |

---

## **License**

This project is licensed under the Apache 2.0 license - see the [LICENSE](LICENSE) file for more information.