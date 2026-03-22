import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_dir = get_package_share_directory('pb_option1_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    amcl_params = LaunchConfiguration('amcl_params')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')
    initial_pose_x = LaunchConfiguration('initial_pose_x')
    initial_pose_y = LaunchConfiguration('initial_pose_y')
    initial_pose_yaw = LaunchConfiguration('initial_pose_yaw')

    declare_use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='false')
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
    declare_initial_pose_x = DeclareLaunchArgument(
        'initial_pose_x',
        default_value='2.0',
        description='Initial AMCL x position in the map frame.')
    declare_initial_pose_y = DeclareLaunchArgument(
        'initial_pose_y',
        default_value='4.0',
        description='Initial AMCL y position in the map frame.')
    declare_initial_pose_yaw = DeclareLaunchArgument(
        'initial_pose_yaw',
        default_value='0.0',
        description='Initial AMCL yaw in radians.')

    configured_amcl_params = ParameterFile(
        RewrittenYaml(
            source_file=amcl_params,
            param_rewrites={
                'use_sim_time': use_sim_time,
                'initial_pose.x': initial_pose_x,
                'initial_pose.y': initial_pose_y,
                'initial_pose.yaw': initial_pose_yaw,
            },
            convert_types=True,
        ),
        allow_substs=True,
    )

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time, 'yaml_filename': map_yaml}],
        arguments=['--ros-args', '--log-level', log_level],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[configured_amcl_params],
        arguments=['--ros-args', '--log-level', log_level],
    )

    lifecycle = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': autostart},
            {'node_names': ['map_server', 'amcl']},
        ],
        arguments=['--ros-args', '--log-level', log_level],
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_map,
        declare_amcl_params,
        declare_autostart,
        declare_log_level,
        declare_initial_pose_x,
        declare_initial_pose_y,
        declare_initial_pose_yaw,
        map_server,
        amcl,
        lifecycle,
    ])
