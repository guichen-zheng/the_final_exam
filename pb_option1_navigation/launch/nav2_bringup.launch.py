import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('pb_option1_navigation')

    # NOTE:
    # To avoid launch creating a temporary /tmp/launch_params_* file (which can introduce
    # non-standard YAML tags and type issues), we only pass params_file to each node.
    # Put `use_sim_time: true/false` directly in your yaml configs if needed.

    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')

    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_dir, 'config', 'nav2_params.yaml'),
        description='Nav2 params yaml')

    declare_autostart = DeclareLaunchArgument('autostart', default_value='true')
    declare_log_level = DeclareLaunchArgument('log_level', default_value='info')
    declare_cmd_vel_topic = DeclareLaunchArgument(
        'cmd_vel_topic', default_value='/cmd_vel',
        description='Where Nav2 outputs velocity. Set to /cmd_vel_nav if you use a mux.')

    controller = Node(
        package='nav2_controller', executable='controller_server', name='controller_server',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
        remappings=[('cmd_vel', cmd_vel_topic)],
    )

    planner = Node(
        package='nav2_planner', executable='planner_server', name='planner_server',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
    )

    smoother = Node(
        package='nav2_smoother', executable='smoother_server', name='smoother_server',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
    )

    behaviors = Node(
        package='nav2_behaviors', executable='behavior_server', name='behavior_server',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
    )

    bt_nav = Node(
        package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
    )

    waypoint = Node(
        package='nav2_waypoint_follower', executable='waypoint_follower', name='waypoint_follower',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
    )

    vel_smoother = Node(
        package='nav2_velocity_smoother', executable='velocity_smoother', name='velocity_smoother',
        output='screen', parameters=[params_file],
        arguments=['--ros-args', '--log-level', log_level],
        remappings=[('cmd_vel', cmd_vel_topic)],
    )

    lifecycle = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_nav2', output='screen',
        parameters=[
            {'autostart': autostart},
            {'node_names': [
                'controller_server', 'planner_server', 'smoother_server',
                'behavior_server', 'bt_navigator', 'waypoint_follower', 'velocity_smoother'
            ]},
        ],
        arguments=['--ros-args', '--log-level', log_level],
    )

    return LaunchDescription([
        declare_params_file,
        declare_autostart,
        declare_log_level,
        declare_cmd_vel_topic,
        controller,
        planner,
        smoother,
        behaviors,
        bt_nav,
        waypoint,
        vel_smoother,
        lifecycle,
    ])
