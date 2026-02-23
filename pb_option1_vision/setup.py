from setuptools import setup
import os
from glob import glob

package_name = 'pb_option1_vision'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'models'), glob('models/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='YOLO-based vision system',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'object_detector_node=pb_option1_vision.object_detector:main',
            'command_interpreter_node=pb_option1_vision.command_interpreter_node:main',
            'follow_behavior_node=pb_option1_vision.follow_behavior_node:main',
        ],
    },
)
