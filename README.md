# the_final_exam
## 总的框架如下
文件结构如下：
```
pb_option1_nav_vision/
├── pb_option1_bringup/               # 启动文件集合
│   ├── launch/
│   │   ├── sim.launch.py             # 仿真启动
│   │   ├── real.launch.py            # 实车启动
│   │   └── joystick.launch.py        # 可选：手柄遥控调试用
│
├── pb_option1_description/           # URDF / xacro 机器人模型（基本保持原样）
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
├── src/
│   ├── object_detector_node.cpp    # 主节点：检测物体
│   ├── follow_behavior_node.cpp    # 跟随逻辑
│   └── command_interpreter_node.cpp # 物体 → 动作映射
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
### 一、pb_option1_bringup
存放launch启动文件
#### 1.sim.launch.py
用于启动仿真（如需小车，请先执行下面pb_option1_description中的内容）
以下是启动视觉仿真流程
1. 编译
```
colcon build --symlink-install
```
2. 启动
```
source install/setup.bash
ros2 launch pb_option1_bringup sim.launch.py
```
3. 在rviz中添加/detection/image_annotated/image
识别到的物品会在终端中给出（problem：在未放物品时持续检测到香蕉？）
### 二、pb_option1_description
由于次模型利用了特殊的xmacro文件，需要特定库将其解释，而且此解释库不可保存在git,所以需要在每次运行有关使用小车模型的调试时，请先执行以下步骤
1. 下载所用依赖
```
sudo apt install git-lfs
pip install vcstool2
```
2. 将相关库导入(在workspace下运行)
```
cd src/pb_option1_description
vcs import --recursive < dependencies.repos
mv joint_state_publisher rmoss_gz_resources sdformat_tools ..
cd ../..
```
3. 下载xmacro插件
```
pip install xmacro
```
### 三、 pb_option1_navigation
### 四、 pb_option1_vision
#### 调试流程：
1. 编译
```
colcon build --packages-select pb_option1_vision
```
2. 先开启另一终端，启动相机节点(ros2自带实例)
```
ros2 run image_tools cam2image --ros-args -p device_id:=0
```
3. 回到原终端（在rviz中加入topic/vision/annotated_image）
```
source install/setup.bash
ros2 launch pb_option1_vision vision_and_follow.launch.py
```
