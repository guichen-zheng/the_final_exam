import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('pb_option1_navigation')

    # NOTE:
    # To avoid launch creating a temporary /tmp/launch_params_* file, we only pass the yaml file
    # as parameters. Put `use_sim_time: true/false` directly inside slam_params.yaml if needed.

    slam_params = LaunchConfiguration('slam_params')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')
    slam_mode = LaunchConfiguration('slam_mode')

    declare_slam_params = DeclareLaunchArgument(
        'slam_params',
        default_value=os.path.join(pkg_dir, 'config', 'slam_params.yaml'),
        description='slam_toolbox parameter yaml')

    declare_autostart = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Autostart lifecycle nodes')

    declare_log_level = DeclareLaunchArgument(
        'log_level', default_value='info',
        description='Log level')

    declare_slam_mode = DeclareLaunchArgument(
        'slam_mode', default_value='async',
        description='slam_toolbox executable: async or sync')

    async_slam = Node(
        condition=IfCondition(PythonExpression(["'", slam_mode, "' == 'async'"])),
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params],
        arguments=['--ros-args', '--log-level', log_level],
    )

    sync_slam = Node(
        condition=IfCondition(PythonExpression(["'", slam_mode, "' == 'sync'"])),
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params],
        arguments=['--ros-args', '--log-level', log_level],
    )

    map_saver = Node(
        package='nav2_map_server',
        executable='map_saver_server',
        name='map_saver_server',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
    )

    lifecycle = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_slam',
        output='screen',
        parameters=[
            {'autostart': autostart},
            {'node_names': ['map_saver_server']},
        ],
        arguments=['--ros-args', '--log-level', log_level],
    )

    return LaunchDescription([
        declare_slam_params,
        declare_autostart,
        declare_log_level,
        declare_slam_mode,
        async_slam,
        sync_slam,
        map_saver,
        lifecycle,
    ])
