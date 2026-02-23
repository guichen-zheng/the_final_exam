#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PythonExpression


def generate_launch_description():
    pkg_share = FindPackageShare('pb_option1_vision')
    
    # 配置文件
    detector_params = PathJoinSubstitution([pkg_share, 'config', 'detector_params.yaml'])
    follow_params = PathJoinSubstitution([pkg_share, 'config', 'follow_params.yaml'])
    
    # Launch参数
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='command',
        description='运行模式: command(命令控制) 或 follow(跟随)'
    )
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='使用仿真时间'
    )
    
    # 物体检测节点
    detector_node = Node(
        package='pb_option1_vision',
        executable='object_detector_node',
        name='object_detector_node',
        output='screen',
        parameters=[
            detector_params,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )
    
    # 命令解释节点 (命令模式)
    command_node = Node(
        package='pb_option1_vision',
        executable='command_interpreter_node',
        name='command_interpreter_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(
        PythonExpression(["'", LaunchConfiguration('mode'), "' == 'command'"])),
    )
    
    # 跟随节点 (跟随模式)
    follow_node = Node(
        package='pb_option1_vision',
        executable='follow_behavior_node',
        name='follow_behavior_node',
        output='screen',
        parameters=[
            follow_params,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        condition=IfCondition(
        PythonExpression(["'", LaunchConfiguration('mode'), "' == 'follow'"])),
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_vision',
        arguments=['-d', '$(find-pkg-share pb_option1_vision)/config/vision.rviz'],
        output='screen',
    )

    return LaunchDescription([
        mode_arg,
        use_sim_time_arg,
        detector_node,
        command_node,
        follow_node,
        rviz_node,
    ])
