from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    gui = LaunchConfiguration('gui')
    server = LaunchConfiguration('server')
    world = LaunchConfiguration('world')

    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Whether to start Gazebo Classic client (gzclient).',
    )
    declare_server = DeclareLaunchArgument(
        'server',
        default_value='true',
        description='Whether to start Gazebo Classic server (gzserver).',
    )
    declare_world = DeclareLaunchArgument(
        'world',
        default_value='empty.world',
        description='Gazebo Classic world file name.',
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world,
            'gui': gui,
            'server': server,
        }.items()
    )

    return LaunchDescription([
        declare_gui,
        declare_server,
        declare_world,
        gazebo,
    ])
