import os
import shutil

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, Shutdown, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_sim = get_package_share_directory('pb_option1_sim')
    pkg_description = get_package_share_directory('pb_option1_description')
    pkg_rmoss_resources = get_package_share_directory('rmoss_gz_resources')
    workspace_root = os.path.abspath(os.path.join(pkg_sim, '..', '..', '..', '..'))
    external_models = os.path.join(workspace_root, 'resource', 'models')
    default_world = os.path.join(workspace_root, 'resource', 'worlds', 'rmuc_2025_world.sdf')
    description_models = os.path.join(pkg_description, 'resource', 'models')
    rmoss_models = os.path.join(pkg_rmoss_resources, 'resource', 'models')

    gui = LaunchConfiguration('gui')
    world = LaunchConfiguration('world')

    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Whether to start the GZ Sim GUI.',
    )
    declare_world = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Absolute path to the GZ Sim world file.',
    )

    ign_resource_path = SetEnvironmentVariable(
        'IGN_GAZEBO_RESOURCE_PATH',
        value=[
            external_models,
            ':',
            description_models,
            ':',
            rmoss_models,
            ':',
            EnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', default_value=''),
        ],
    )
    gz_resource_path = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        value=[
            external_models,
            ':',
            description_models,
            ':',
            rmoss_models,
            ':',
            EnvironmentVariable('GZ_SIM_RESOURCE_PATH', default_value=''),
        ],
    )

    ign_path = shutil.which('ign')

    gz_server = ExecuteProcess(
        cmd=[
            'ruby',
            ign_path,
            'gazebo',
            '-r',
            '-s',
            '--headless-rendering',
            world,
            '--force-version',
            '6',
        ],
        output='screen',
        shell=False,
        on_exit=Shutdown(),
    )

    gz_gui = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ruby',
                    ign_path,
                    'gazebo',
                    '-g',
                    '--force-version',
                    '6',
                ],
                output='screen',
                shell=False,
                condition=IfCondition(gui),
            )
        ],
    )

    return LaunchDescription([
        declare_gui,
        declare_world,
        ign_resource_path,
        gz_resource_path,
        gz_server,
        gz_gui,
    ])
