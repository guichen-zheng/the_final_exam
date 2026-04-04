import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg_description = get_package_share_directory('pb_option1_description')
    pkg_navigation = get_package_share_directory('pb_option1_navigation')
    pkg_bringup = get_package_share_directory('pb_option1_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    mode = LaunchConfiguration('mode')
    robot_name = LaunchConfiguration('robot_name')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    use_vision = LaunchConfiguration('use_vision')
    map_yaml = LaunchConfiguration('map')
    nav2_params = LaunchConfiguration('nav2_params')
    amcl_params = LaunchConfiguration('amcl_params')
    slam_params = LaunchConfiguration('slam_params')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')

    # ================== 实车参数声明 ==================
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',                    # 实车必须为 false
        description='Use simulation clock for all nodes.',
    )

    declare_mode = DeclareLaunchArgument(
        'mode',
        default_value='nav',                      # 实车默认使用导航模式
        description="Mode: 'slam' or 'nav'",
    )

    declare_robot_name = DeclareLaunchArgument(
        'robot_name',
        default_value='pb_robot',
        description='Robot name used for TF.',
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to start RViz.',
    )

    declare_rviz_config_file = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(pkg_description, 'rviz', 'navigation_debug.rviz'),
        description='RViz config file.',
    )

    declare_use_vision = DeclareLaunchArgument(
        'use_vision',
        default_value='false',
        description='Whether to start vision nodes.',
    )

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_navigation, 'maps', 'map.yaml'),
        description='Map YAML used when mode:=nav.',
    )

    declare_nav2_params = DeclareLaunchArgument(
        'nav2_params',
        default_value=os.path.join(pkg_navigation, 'config', 'nav2_params.yaml'),
        description='Nav2 parameter file.',
    )

    declare_amcl_params = DeclareLaunchArgument(
        'amcl_params',
        default_value=os.path.join(pkg_navigation, 'config', 'amcl_params.yaml'),
        description='AMCL parameter file.',
    )

    declare_slam_params = DeclareLaunchArgument(
        'slam_params',
        default_value=os.path.join(pkg_navigation, 'config', 'slam_params.yaml'),
        description='SLAM Toolbox parameter file.',
    )

    declare_cmd_vel_topic = DeclareLaunchArgument(
        'cmd_vel_topic',
        default_value='/cmd_vel',
        description='Velocity topic output from Nav2.',
    )

    # ================== 核心节点（保留原来结构） ==================
    description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'robot_description_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'robot_name': robot_name,
            'use_rviz': use_rviz,
            'rviz_config_file': rviz_config_file,
        }.items(),
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_navigation, 'launch', 'slam.launch.py')
        ),
        condition=IfCondition(PythonExpression(["'", mode, "' == 'slam'"])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params': slam_params,
        }.items(),
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_navigation, 'launch', 'localization.launch.py')
        ),
        condition=IfCondition(PythonExpression(["'", mode, "' == 'nav'"])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_yaml,
            'amcl_params': amcl_params,
        }.items(),
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_navigation, 'launch', 'nav2_bringup.launch.py')
        ),
        condition=IfCondition(PythonExpression(["'", mode, "' == 'nav'"])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params,
            'cmd_vel_topic': cmd_vel_topic,
        }.items(),
    )

    # 可选：实车视觉节点（如果需要再打开）
    usb_cam = Node(
        condition=IfCondition(use_vision),
        package='usb_cam',
        executable='usb_cam_node_exe',
        parameters=[{
            'video_device': '/dev/video0',
            'image_width': 640,
            'image_height': 480,
            'framerate': 30.0,
            'pixel_format': 'yuyv',
            'camera_frame_id': 'camera_link',
        }],
        remappings=[('/image_raw', '/image')],
        output='screen'
    )

    object_detector = Node(
        condition=IfCondition(use_vision),
        package='pb_option1_vision',
        executable='object_detector',
        output='screen'
    )

    follow_behavior = Node(
        condition=IfCondition(use_vision),
        package='pb_option1_vision',
        executable='follow_behavior',
        output='screen'
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_mode,
        declare_robot_name,
        declare_use_rviz,
        declare_rviz_config_file,
        declare_use_vision,
        declare_map,
        declare_nav2_params,
        declare_amcl_params,
        declare_slam_params,
        declare_cmd_vel_topic,
        description_launch,
        slam_launch,
        localization_launch,
        nav2_launch,
        usb_cam,
        object_detector,
        follow_behavior,
    ])