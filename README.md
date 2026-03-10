# the_final_exam
## 总的框架如下
文件结构如下：
```
pb_option1_nav_vision/
├── pb_option1_bringup/               # 启动文件集合
│   ├── launch/
│   │   ├── sim.launch.py             # 仿真启动
│   │   ├── real.launch.py            # 实车启动
│   │   └── joystick.launch.py        
│
├── pb2025_robot_description/           #xmacro 机器人模型（基本保持原样）
│
├── pb_option1_navigation/            # 核心导航部分（从 pb2025_sentry_nav 精简而来）
│   ├── config/
│   │   ├── nav2_params.yaml          # nav2 参数（控制器、规划器、BT等）
│   │   ├── slam_params.yaml          # slam 参数（通常用 cartographer 或 slam_toolbox）
│   │   └── amcl_params.yaml          # 定位参数（仿真和实车可能不同）
│   ├── launch/
│   │   ├── slam.launch.py
│   │   ├── localization.launch.py
│   │   └── nav2_bringup.launch.py
│   └── maps/                         # 保存的地图文件
│
├── pb_option1_vision/                # 新增：视觉识别与物体跟随
├── include/                        # 头文件（可选，如果有自定义类）
│   └── pb_option1_vision/
│       └── object_detector.hpp     # 示例头文件
├── pb_option1_vision/
│   ├── object_detector_node.py    # 主节点：检测物体
│   ├── follow_behavior_node.py    # 跟随逻辑
│   └── command_interpreter_node.py # 物体 → 动作映射
├── config/
│   ├── detector_params.yaml        # HSV 阈值等（用 YAML-cpp 加载）
│   └── follow_params.yaml          # 跟随参数
├── launch/
│   └── vision_and_follow.launch.py # 启动文件仍用 Python（方便）
├── CMakeLists.txt                  # 构建文件（必须，用 ament_cmake）
├── package.xml                     # 包描述（添加 C++ 依赖）
└── README.md
|
├── pb_option1_sim/                   # 仿真专用（基于 pb_rm_simulation 精简）
│   ├── worlds/                       # 自定义仿真场景（放水杯、苹果、香蕉模型等）
│   └── launch/
│       └── gazebo_with_objects.launch.py
└── README.md
```
目前结构如此，后续可作出相应更改
### 一、准备工作
#### 1. 依赖准备（在workspace下）
```sh
vcs import src < src/dependencies.repos
sudo apt install git-lfs
pip install vcstool2
pip install xmacro
```
#### 2.编译
```sh 
colcon build --symlink-install
``` 
##### 如崩溃用这个
```sh
colcon build --symlink-install --parallel-workers 3
```
### 二、启动(vision功能)
#### 启动识别
```sh
ros2 launch pb_option1_bringup sim.launch.py mode:=detect
```
#### 启动跟随
```sh
ros2 launch pb_option1_bringup sim.launch.py mode:=follow
```
##### 在另一终端中启动相机,如想看到识别结果（在rviz中加入topic/vision/annotated_image）
```sh
ros2 run image_tools cam2image --ros-args -p device_id:=0
```
##### 可以启动控制小车
```sh
ros2 run rmoss_gz_base test_chassis_cmd.py --ros-args -r __ns:=/red_standard_robot1/robot_base -p v:=0.3 -p w:=0.3
```
