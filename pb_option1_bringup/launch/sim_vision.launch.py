from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from sdformat_tools.urdf_generator import UrdfGenerator
from xmacro.xmacro4sdf import XMLMacro4sdf
import os

def generate_launch_description():
    pkg_description = get_package_share_directory('pb2025_robot_description')
    pkg_vision = get_package_share_directory('pb_option1_vision')
    pkg_simulator = get_package_share_directory('rmu_gazebo_simulator')
    
    # ================== 新增参数 ==================
    use_existing_sim_arg = DeclareLaunchArgument(
        'use_existing_sim',
        default_value='false',
        description='true = 附加到已启动的 sim.launch.py（跳过 spawn、bridge、rviz 等）'
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='simulation_robot',
        description='机器人名称（附加模式必须设为 nav 里实际的 robot name，通常是 simulation_robot_gz）'
    )

    # ================== 模式选择 ==================
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='detect',
        description='运行模式: "detect" 或 "follow"'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='使用模拟时间'
    )

    # ================== 智能 cmd_vel remap ==================
    target_cmd_vel = PythonExpression([
        "'/cmd_vel' if '", LaunchConfiguration('use_existing_sim'), "' == 'true' ",
        "else '/", LaunchConfiguration('robot_name'), "/cmd_vel'"
    ])

    # ================== Gazebo（仅 standalone） ==================
    gazebo = IncludeLaunchDescription(
        PathJoinSubstitution([pkg_simulator, 'launch', 'gazebo.launch.py']),
        launch_arguments={
            'world_sdf_path': PathJoinSubstitution([
                pkg_simulator, 'resource', 'worlds', 'empty_world.sdf'
            ]),
        }.items(),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    # ================== xmacro + URDF（standalone 需要） ==================
    robot_xmacro_path = os.path.join(
        pkg_description, 'resource', 'xmacro', 'simulation_robot.sdf.xmacro'
    )

    xmacro = XMLMacro4sdf()
    xmacro.set_xml_file(robot_xmacro_path)
    xmacro.generate({"global_initial_color": "red"})
    robot_xml = xmacro.to_string()

    urdf_generator = UrdfGenerator()
    urdf_generator.parse_from_sdf_string(robot_xml)
    robot_urdf_xml = urdf_generator.to_string()

    # ================== 核心节点（已加 condition + 动态 robot_name） ==================
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_xml,
            '-name', LaunchConfiguration('robot_name'),
            '-allow_renaming', 'true',
            '-x', '0', '-y', '0', '-z', '0.1', '-Y', '0',
        ],
        output='screen',
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=LaunchConfiguration('robot_name'),
        parameters=[{'robot_description': robot_urdf_xml, 'use_sim_time': LaunchConfiguration('use_sim_time')}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        output='screen',
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    robot_base = Node(
        package='rmoss_gz_base',
        executable='rmua19_robot_base',
        name='rmua19_robot_base',
        namespace=LaunchConfiguration('robot_name'),
        parameters=[
            os.path.join(pkg_simulator, 'config', 'base_params.yaml'),
            {'robot_name': LaunchConfiguration('robot_name')}
        ],
        output='screen',
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    # ================== 视觉节点（保持你原来的逻辑） ==================
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
        remappings=[('/cmd_vel', target_cmd_vel)],
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
        remappings=[('/cmd_vel', target_cmd_vel)],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('mode'), "' == 'follow'"]))
    )

    # ================== Bridge（仅 standalone） ==================
    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            PythonExpression(["/", LaunchConfiguration('robot_name'), "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist"]),
            '--ros-args', '--log-level', 'info'
        ],
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/image'],
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    # ================== 描述 + RViz（仅 standalone） ==================
    description_launch = IncludeLaunchDescription(
        PathJoinSubstitution([
            pkg_description, 'launch', 'robot_description_launch.py'
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_rviz': 'true'
        }.items(),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('use_existing_sim'), "' == 'false'"]))
    )

    ld = LaunchDescription([
        mode_arg,
        use_sim_time_arg,
        use_existing_sim_arg,
        robot_name_arg,
        gazebo,
        spawn_robot,
        robot_state_publisher,
        robot_base,
        object_detector,
        command_interpreter,
        follow_behavior,
        cmd_vel_bridge,
        image_bridge,
        description_launch,
    ])

    return ld