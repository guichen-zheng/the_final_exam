from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression
import os

def generate_launch_description():
    pkg_description = get_package_share_directory('pb_option1_description')
    pkg_sim = get_package_share_directory('pb_option1_sim')
    pkg_vision = get_package_share_directory('pb_option1_vision')

    # 新增：模式选择参数
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='detect',
        description='运行模式: "detect"（判断物体类型转弯/直行） 或 "follow"（跟随物体移动）'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='使用模拟时间'
    )

    # 1. 机器人描述 + RViz
    description_launch = IncludeLaunchDescription(
        PathJoinSubstitution([
            pkg_description, 'launch', 'robot_description_launch.py'
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_rviz': 'true'
        }.items()
    )

    # 2. Gazebo
    gazebo = IncludeLaunchDescription(
        PathJoinSubstitution([
            pkg_sim, 'launch', 'gazebo_with_objects.launch.py'
        ])
    )

    # 3. Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'simulation_robot',  # 注意这里用 simulation_robot，与模型名一致
            '-x', '0',
            '-y', '0',
            '-z', '0.6',  # 建议保持或更高，避免卡地
            '-Y', '0',
            '-timeout', '30'
        ],
        output='screen'
    )

    # 4. 视觉节点
    detector_params = PathJoinSubstitution([pkg_vision, 'config', 'detector_params.yaml'])
    follow_params = PathJoinSubstitution([pkg_vision, 'config', 'follow_params.yaml'])

    object_detector = Node(
        package='pb_option1_vision',
        executable='object_detector_node',
        name='object_detector_node',
        output='screen',
        parameters=[
            detector_params,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )

    # 只在 detect 模式启动命令解释节点
    command_interpreter = Node(
        package='pb_option1_vision',
        executable='command_interpreter_node',
        name='command_interpreter_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('mode'), "' == 'detect'"]))
    )

    # 只在 follow 模式启动跟随节点
    follow_behavior = Node(
        package='pb_option1_vision',
        executable='follow_behavior_node',
        name='follow_behavior_node',
        output='screen',
        parameters=[
            follow_params,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('mode'), "' == 'follow'"]))
    )

    # 可选：视觉专用 RViz（已注释，如果你需要可打开）
    # vision_rviz = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2_vision',
    #     arguments=['-d', PathJoinSubstitution([pkg_vision, 'config', 'vision.rviz'])],
    #     output='screen'
    # )

    # Bridge for cmd_vel (ROS /cmd_vel to Gazebo /model/simulation_robot/cmd_vel, ROS to GZ direction)
    image_bridge = Node(
    package='ros_gz_image',
    executable='image_bridge',
    arguments=['/image'],  # 你的 webcam 话题
    output='screen',
    parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '--log-level', 'info'],
        output='screen',
        parameters=[
            {"bridge_names": ["cmd_vel_bridge"]},
            {"bridges.cmd_vel_bridge.ros_topic_name": "/cmd_vel"},
            {"bridges.cmd_vel_bridge.gz_topic_name": "/model/simulation_robot/cmd_vel"},  # 匹配默认插件订阅
            {"bridges.cmd_vel_bridge.ros_type_name": "geometry_msgs/msg/Twist"},
            {"bridges.cmd_vel_bridge.gz_type_name": "gz.msgs.Twist"},  # 用 gz.msgs
            {"bridges.cmd_vel_bridge.direction": "ROS_TO_GZ"},
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )

    return LaunchDescription([
        mode_arg,
        use_sim_time_arg,
        description_launch,
        gazebo,
        spawn_robot,
        object_detector,
        command_interpreter,
        follow_behavior,
        cmd_vel_bridge,
        image_bridge,
        # vision_rviz,
    ])