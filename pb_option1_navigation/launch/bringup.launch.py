#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import PushRosNamespace


def generate_launch_description():
    pkg_nav = get_package_share_directory('pb_option1_navigation')

    # --- launch args ---
    mode = LaunchConfiguration('mode')  # slam | localization
    use_sim_time = LaunchConfiguration('use_sim_time')
    namespace = LaunchConfiguration('namespace')

    params_file = LaunchConfiguration('params_file')
    slam_params = LaunchConfiguration('slam_params')
    slam_params = LaunchConfiguration('slam_params')
    map_yaml = LaunchConfiguration('map')

    # default files
    default_nav2_params = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')
    default_slam_params = os.path.join(pkg_nav, 'config', 'slam_params.yaml')
    default_amcl_params = os.path.join(pkg_nav, 'config', 'amcl_params.yaml')
    default_map_yaml = os.path.join(pkg_nav, 'maps', 'map.yaml')

    # include targets
    slam_launch = os.path.join(pkg_nav, 'launch', 'slam.launch.py')
    localization_launch = os.path.join(pkg_nav, 'launch', 'localization.launch.py')
    nav2_launch = os.path.join(pkg_nav, 'launch', 'nav2_bringup.launch.py')

    # mode switch: slam => mode_is_slam true, otherwise false
    mode_is_slam = LaunchConfiguration('mode_is_slam')

    # --- group: SLAM (mapping) ---
    slam_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(slam_launch),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'slam_params': slam_params,
                }.items()
            )
        ],
        condition=IfCondition(mode_is_slam),
    )

    # --- group: Localization (map_server + amcl) ---
    localization_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(localization_launch),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'map': map_yaml,
                    'slam_params': slam_params,
                }.items()
            )
        ],
        condition=UnlessCondition(mode_is_slam),
    )

    # --- group: Nav2 (planner/controller/bt navigator...) ---
    nav2_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(nav2_launch),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'params_file': params_file,
                }.items()
            )
        ]
    )

    # Optional namespace wrapper
    # If you don't use namespace, keep default empty and this does nothing.
    all_group = GroupAction(
        actions=[
            PushRosNamespace(namespace),
            slam_group,
            localization_group,
            nav2_group,
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'mode',
            default_value='slam',
            description="Run mode: 'slam' for mapping, 'localization' for using a saved map.",
        ),
        # 用一个布尔开关来做 IfCondition（IfCondition不支持直接比较字符串）
        DeclareLaunchArgument(
            'mode_is_slam',
            default_value=TextSubstitution(text='true'),
            description="Internal flag. true => run SLAM. false => run localization.",
        ),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('namespace', default_value=''),

        DeclareLaunchArgument('params_file', default_value=default_nav2_params),
        DeclareLaunchArgument('slam_params', default_value=default_slam_params),
        DeclareLaunchArgument('slam_params', default_value=default_amcl_params),
        DeclareLaunchArgument('map', default_value=default_map_yaml),

        all_group,
    ])