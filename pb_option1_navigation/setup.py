from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'pb_option1_navigation'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'behavior_trees'), glob('behavior_trees/*.xml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='马蕴灵',
    maintainer_email='mayunling20070811@gmail.com',
    description='Option1 navigation bringup (SLAM / localization / Nav2).',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gz_frame_normalizer = pb_option1_navigation.gz_frame_normalizer:main',
        ],
    },
)
