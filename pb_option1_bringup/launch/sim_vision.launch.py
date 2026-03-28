from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from nav2_common.launch import ReplaceString   # 官方替换 <robot_name> 用
from sdformat_tools.urdf_generator import UrdfGenerator
from xmacro.xmacro4sdf import XMLMacro4sdf
import os

def generate_launch_description():
    pkg_description = get_package_share_directory('pb2025_robot_description')
    pkg_vision = get_package_share_directory('pb_option1_vision')
    pkg_simulator = get_package_share_directory('rmu_gazebo_simulator')

    # ================== 模式选择（和你原来 100% 一样） ==================
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

    robot_name = 'simulation_robot'

    # # ================== 官方 Gazebo（第一版 B 路线） ==================
    # gazebo = IncludeLaunchDescription(
    #     PathJoinSubstitution([
    #         pkg_simulator, 'launch', 'gazebo.launch.py'
    #     ]),
    #     launch_arguments={
    #         'world_sdf_path': PathJoinSubstitution([
    #             pkg_simulator, 'resource', 'worlds', 'empty_world.sdf'
    #         ]),
    #     }.items()
    # )

    # ================== Spawn（官方 create + 你的 xmacro） ==================
    robot_xmacro_path = os.path.join(
        pkg_description, 'resource', 'xmacro', 'simulation_robot.sdf.xmacro'
    )

    xmacro = XMLMacro4sdf()
    xmacro.set_xml_file(robot_xmacro_path)

    xmacro.generate({"global_initial_color": "red"})  # 或你需要的颜色/参数，空 dict 也行试试

    robot_xml = xmacro.to_string()  # 这就是展开后的 SDF 字符串

    # SDF → URDF（给 robot_state_publisher 用）
    urdf_generator = UrdfGenerator()
    urdf_generator.parse_from_sdf_string(robot_xml)
    robot_urdf_xml = urdf_generator.to_string()

    # spawn 用 SDF 字符串
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_xml,  # ← 用展开后的
            '-name', robot_name,
            '-allow_renaming', 'true',
            '-x', '0', '-y', '0', '-z', '0.1', '-Y', '0',
        ],
        output='screen'
    )

    # 额外：把 URDF 发布给 robot_state_publisher（如果你原来的 description_launch 没处理）
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=robot_name,
        parameters=[{'robot_description': robot_urdf_xml, 'use_sim_time': LaunchConfiguration('use_sim_time')}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        output='screen'
    )


    # ================== 官方底盘控制（B 路线的核心） ==================
    robot_base = Node(
        package='rmoss_gz_base',
        executable='rmua19_robot_base',
        name='rmua19_robot_base',
        namespace=robot_name,
        parameters=[
            os.path.join(pkg_simulator, 'config', 'base_params.yaml'),
            {'robot_name': robot_name}
        ],
        output='screen'
    )

    # ================== 你的视觉节点（保持原来结构） ==================
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

    command_interpreter = Node(
        package='pb_option1_vision',
        executable='command_interpreter_node',
        name='command_interpreter_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        remappings=[('/cmd_vel', '/simulation_robot/cmd_vel')], 
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('mode'), "' == 'detect'"]))
    )

    follow_behavior = Node(
        package='pb_option1_vision',
        executable='follow_behavior_node',
        name='follow_behavior_node',
        output='screen',
        parameters=[
            follow_params,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        remappings=[('/cmd_vel', '/simulation_robot/cmd_vel')],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('mode'), "' == 'follow'"]))
    )

    # ================== Bridge ==================
    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            f'/{robot_name}/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',   # ← 改成这个
            '--ros-args', '--log-level', 'info'
        ],
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/image'],
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # ================== 描述 + RViz（你原来的） ==================
    # description_launch = IncludeLaunchDescription(
    #     PathJoinSubstitution([
    #         pkg_description, 'launch', 'robot_description_launch.py'
    #     ]),
    #     launch_arguments={
    #         'use_sim_time': LaunchConfiguration('use_sim_time'),
    #         'use_rviz': 'true'
    #     }.items()
    # )
    
    ld = LaunchDescription([
        mode_arg,
        use_sim_time_arg,
        spawn_robot,
        robot_base,               # 官方底盘
        object_detector,
        command_interpreter,
        follow_behavior,
        cmd_vel_bridge,
        image_bridge,
        robot_state_publisher,
    ])

    return ld