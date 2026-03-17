import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_sim = get_package_share_directory('pb_option1_sim')

    gui = LaunchConfiguration('gui')
    world = LaunchConfiguration('world')

    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Whether to start the GZ Sim GUI.',
    )
    declare_world = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_sim, 'worlds', 'gz_nav_empty.sdf'),
        description='Absolute path to the GZ Sim world file.',
    )

    gz_args = PythonExpression([
        "'-r ' + '",
        world,
        "' if '",
        gui,
        "' == 'true' else '-r -s --headless-rendering ' + '",
        world,
        "'",
    ])

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': gz_args,
        }.items(),
    )

    return LaunchDescription([
        declare_gui,
        declare_world,
        gz_sim,
    ])
