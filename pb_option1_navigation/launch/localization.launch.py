import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('pb_option1_navigation')

    # NOTE:
    # To avoid launch creating a temporary /tmp/launch_params_* file, we do not pass dict-style
    # overrides (like use_sim_time) here. Put `use_sim_time: true/false` inside amcl_params.yaml
    # and/or other yaml configs if needed.

    map_yaml = LaunchConfiguration('map')
    amcl_params = LaunchConfiguration('amcl_params')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_dir, 'maps', 'map.yaml'),
        description='Full path to map yaml')
    declare_amcl_params = DeclareLaunchArgument(
        'amcl_params',
        default_value=os.path.join(pkg_dir, 'config', 'amcl_params.yaml'),
        description='AMCL params yaml')
    declare_autostart = DeclareLaunchArgument('autostart', default_value='true')
    declare_log_level = DeclareLaunchArgument('log_level', default_value='info')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map_yaml}],
        arguments=['--ros-args', '--log-level', log_level],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params],
        arguments=['--ros-args', '--log-level', log_level],
    )

    lifecycle = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'autostart': autostart},
            {'node_names': ['map_server', 'amcl']},
        ],
        arguments=['--ros-args', '--log-level', log_level],
    )

    return LaunchDescription([
        declare_map,
        declare_amcl_params,
        declare_autostart,
        declare_log_level,
        map_server,
        amcl,
        lifecycle,
    ])
