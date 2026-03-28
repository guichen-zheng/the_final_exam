import os
import tempfile
import time

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler, TimerAction
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.logging import get_logger
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
import rclpy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from xmacro.xmacro4sdf import XMLMacro4sdf


def generate_launch_description():
    pkg_description = get_package_share_directory('pb_option1_description')
    pkg_navigation = get_package_share_directory('pb_option1_navigation')
    pkg_sim = get_package_share_directory('pb_option1_sim')
    pkg_bringup = get_package_share_directory('pb_option1_bringup')
    workspace_root = os.path.abspath(os.path.join(pkg_sim, '..', '..', '..', '..'))
    default_world = os.path.join(workspace_root, 'src','rmu_gazebo_simulator','rmu_gazebo_simulator','resource', 'worlds', 'rmuc_2025_world.sdf')

    use_sim_time = LaunchConfiguration('use_sim_time')
    mode = LaunchConfiguration('mode')
    robot_name = LaunchConfiguration('robot_name')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    use_vision = LaunchConfiguration('use_vision')
    gazebo_gui = LaunchConfiguration('gazebo_gui')
    map_yaml = LaunchConfiguration('map')
    nav2_params = LaunchConfiguration('nav2_params')
    amcl_params = LaunchConfiguration('amcl_params')
    slam_params = LaunchConfiguration('slam_params')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')
    world = LaunchConfiguration('world')
    world_name = LaunchConfiguration('world_name')
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')
    spawn_yaw = LaunchConfiguration('spawn_yaw')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock for all nodes.',
    )
    declare_mode = DeclareLaunchArgument(
        'mode',
        default_value='slam',
        description="Simulation mode: 'slam', 'nav', or 'base'.",
    )
    declare_robot_name = DeclareLaunchArgument(
        'robot_name',
        default_value='simulation_robot_gz',
        description='Robot xmacro name used for TF publishing and GZ Sim spawn.',
    )
    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to start RViz from the description launch.',
    )
    declare_rviz_config_file = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(pkg_description, 'rviz', 'navigation_debug.rviz'),
        description='RViz config file used by the description launch.',
    )
    declare_use_vision = DeclareLaunchArgument(
        'use_vision',
        default_value='false',
        description='Whether to start usb_cam and vision follow nodes.',
    )
    declare_gazebo_gui = DeclareLaunchArgument(
        'gazebo_gui',
        default_value='true',
        description='Whether to start the GZ Sim GUI.',
    )
    declare_world = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Absolute path to the GZ Sim world file.',
    )
    declare_world_name = DeclareLaunchArgument(
        'world_name',
        default_value='default',
        description='World name declared inside the GZ Sim world SDF.',
    )
    declare_spawn_x = DeclareLaunchArgument(
        'spawn_x',
        default_value='2.0',
        description='Robot spawn x position in the GZ Sim world.',
    )
    declare_spawn_y = DeclareLaunchArgument(
        'spawn_y',
        default_value='4.0',
        description='Robot spawn y position in the GZ Sim world.',
    )
    declare_spawn_z = DeclareLaunchArgument(
        'spawn_z',
        default_value='0.35',
        description='Robot spawn z position in the GZ Sim world.',
    )
    declare_spawn_yaw = DeclareLaunchArgument(
        'spawn_yaw',
        default_value='1.5708',
        description='Robot spawn yaw in radians in the GZ Sim world.',
    )
    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_navigation, 'maps', 'map.yaml'),
        description='Map YAML used when mode:=nav.',
    )
    declare_nav2_params = DeclareLaunchArgument(
        'nav2_params',
        default_value=os.path.join(pkg_navigation, 'config', 'nav2_params.yaml'),
        description='Nav2 parameter file used when mode:=nav.',
    )
    declare_amcl_params = DeclareLaunchArgument(
        'amcl_params',
        default_value=os.path.join(pkg_navigation, 'config', 'amcl_params.yaml'),
        description='AMCL parameter file used when mode:=nav.',
    )
    declare_slam_params = DeclareLaunchArgument(
        'slam_params',
        default_value=os.path.join(pkg_navigation, 'config', 'slam_params.yaml'),
        description='SLAM Toolbox parameter file used when mode:=slam.',
    )
    declare_cmd_vel_topic = DeclareLaunchArgument(
        'cmd_vel_topic',
        default_value='/cmd_vel',
        description='Velocity topic output from Nav2.',
    )

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

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, 'launch', 'gz_sim_with_objects.launch.py')
        ),
        launch_arguments={
            'gui': gazebo_gui,
            'world': world,
        }.items(),
    )

    bridge_config = os.path.join(pkg_bringup, 'config', 'gz_bridges.yaml')

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_config,
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen',
    )

    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/model/pb_robot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'],
        remappings=[('/model/pb_robot/cmd_vel', cmd_vel_topic)],
        output='screen',
    )

    frame_normalizer = Node(
        package='pb_option1_navigation',
        executable='gz_frame_normalizer',
        parameters=[{
            'input_scan_topic': '/scan_raw',
            'output_scan_topic': '/scan',
            'input_odom_topic': '/odom_raw',
            'output_odom_topic': '/odom',
            'scan_frame_id': 'front_rplidar_a2',
            'odom_frame_id': 'odom',
            'base_frame_id': 'base_footprint',
        }],
        output='screen',
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
            'initial_pose_x': spawn_x,
            'initial_pose_y': spawn_y,
            'initial_pose_yaw': spawn_yaw,
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

    def wait_for_sim_topics_and_start(context, *args, **kwargs):
        requested_mode = context.launch_configurations['mode']
        required_topics = {}
        if requested_mode == 'slam':
            required_topics = {'/scan_raw': LaserScan}
        elif requested_mode == 'nav':
            required_topics = {
                '/odom_raw': Odometry,
                '/scan_raw': LaserScan,
            }

        if not required_topics:
            return [slam_launch, localization_launch, nav2_launch, usb_cam, object_detector, follow_behavior]

        logger = get_logger('pb_option1_gz_waiter')
        initialized_here = False
        waiter = None
        subscriptions = []
        received_topics = {topic_name: False for topic_name in required_topics}
        timeout_sec = 120.0
        start_time = time.monotonic()
        last_reported_missing = None

        try:
            if not rclpy.ok():
                rclpy.init(args=[])
                initialized_here = True

            waiter = rclpy.create_node('pb_option1_gz_waiter')

            for topic_name, topic_type in required_topics.items():
                subscriptions.append(
                    waiter.create_subscription(
                        topic_type,
                        topic_name,
                        lambda _msg, topic=topic_name: received_topics.__setitem__(topic, True),
                        10,
                    )
                )

            while time.monotonic() - start_time < timeout_sec:
                missing = [topic for topic, received in received_topics.items() if not received]
                if not missing:
                    logger.info(
                        f"Received GZ simulation messages on {list(required_topics.keys())}; starting mode '{requested_mode}'."
                    )
                    break

                if missing != last_reported_missing:
                    logger.info(f"Waiting for GZ simulation messages before startup: {missing}")
                    last_reported_missing = missing

                rclpy.spin_once(waiter, timeout_sec=0.5)
            else:
                logger.warning(
                    f"Timed out after {timeout_sec:.0f}s waiting for messages on {list(required_topics.keys())}; starting anyway."
                )
        finally:
            if waiter is not None:
                waiter.destroy_node()
            if initialized_here and rclpy.ok():
                rclpy.shutdown()

        return [slam_launch, localization_launch, nav2_launch, usb_cam, object_detector, follow_behavior]

    def spawn_and_chain_setup(context, *args, **kwargs):
        xmacro_file = os.path.join(
            pkg_description,
            'resource',
            'xmacro',
            f"{context.launch_configurations['robot_name']}.sdf.xmacro",
        )

        xmacro = XMLMacro4sdf()
        xmacro.set_xml_file(xmacro_file)
        xmacro.generate()
        robot_sdf_xml = xmacro.to_string()

        temp_sdf = tempfile.NamedTemporaryFile(
            mode='w',
            prefix='pb_option1_gz_',
            suffix='.sdf',
            delete=False,
        )
        temp_sdf.write(robot_sdf_xml)
        temp_sdf.flush()
        temp_sdf.close()

        spawn_robot = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-world', context.launch_configurations['world_name'],
                '-file', temp_sdf.name,
                '-name', 'pb_robot',
                '-x', context.launch_configurations['spawn_x'],
                '-y', context.launch_configurations['spawn_y'],
                '-z', context.launch_configurations['spawn_z'],
                '-Y', context.launch_configurations['spawn_yaw'],
            ],
            output='screen',
        )

        delayed_start = RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_robot,
                on_exit=[OpaqueFunction(function=wait_for_sim_topics_and_start)],
            )
        )

        delayed_spawn = TimerAction(
            period=2.0,
            actions=[spawn_robot],
        )

        return [delayed_spawn, delayed_start]

    return LaunchDescription([
        declare_use_sim_time,
        declare_mode,
        declare_robot_name,
        declare_use_rviz,
        declare_rviz_config_file,
        declare_use_vision,
        declare_gazebo_gui,
        declare_world,
        declare_world_name,
        declare_spawn_x,
        declare_spawn_y,
        declare_spawn_z,
        declare_spawn_yaw,
        declare_map,
        declare_nav2_params,
        declare_amcl_params,
        declare_slam_params,
        declare_cmd_vel_topic,
        description_launch,
        gz_sim,
        bridge_node,
        cmd_vel_bridge,
        frame_normalizer,
        OpaqueFunction(function=spawn_and_chain_setup),
    ])
