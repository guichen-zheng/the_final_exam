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
存放 launch 启动文件。

#### 1. 当前入口说明
当前有两条仿真入口：

- `sim.launch.py`
  - 默认仿真总入口
  - 当前已切到 GZ Sim
  - 支持 `mode:=base`、`mode:=slam`、`mode:=nav`
- `sim_gz.launch.py`
  - GZ Sim 兼容入口
  - 支持 `mode:=base`、`mode:=slam`、`mode:=nav`

两条入口都会：

- 启动机器人描述和 RViz
- 生成临时 SDF 并把机器人 spawn 到仿真器
- 在 `slam` / `nav` 模式下等待关键话题就绪后再继续启动对应功能
- 当前 GZ Sim 路径会把 server 和 GUI 分开启动，减少较大比赛场地下 GUI 黑屏卡死的问题

#### 2. 当前推荐启动方式
1. 编译
```bash
colcon build --symlink-install
```

2. source 环境

如果你使用 `zsh`：
```bash
source install/setup.zsh
```

如果你使用 `bash`：
```bash
source install/setup.bash
```

如果你平时开着 Conda，建议先执行：
```bash
conda deactivate
```

3. 启动

默认基础仿真：
```bash
ros2 launch pb_option1_bringup sim.launch.py mode:=base
```

如需调整默认出生点，可额外传：
```bash
ros2 launch pb_option1_bringup sim.launch.py mode:=base spawn_x:=2.0 spawn_y:=4.0 spawn_yaw:=1.5708
```

在 `mode:=nav` 下，AMCL 默认初始位姿会自动跟随 `spawn_x`、`spawn_y`、`spawn_yaw`。

默认建图仿真：
```bash
ros2 launch pb_option1_bringup sim.launch.py mode:=slam
```

默认导航仿真：
```bash
ros2 launch pb_option1_bringup sim.launch.py mode:=nav
```

兼容入口基础仿真：
```bash
ros2 launch pb_option1_bringup sim_gz.launch.py mode:=base
```

兼容入口建图仿真：
```bash
ros2 launch pb_option1_bringup sim_gz.launch.py mode:=slam
```

兼容入口导航仿真：
```bash
ros2 launch pb_option1_bringup sim_gz.launch.py mode:=nav
```
保存地图
```
ros2 launch pb_option1_bringup real.launch.py mode:=nav map:=~/my_map.yaml
```

#### 3. RViz 默认行为
当前 `sim.launch.py` 和 `sim_gz.launch.py` 默认使用导航调试版 RViz 配置：

- 固定坐标系为 `map`
- 默认显示 `/map`、`/scan`、`/odom`、`/plan`、`/local_plan`
- 默认提供 `2D Pose Estimate` 和 `2D Goal Pose`

如果只想看机器人模型，可以手动切回旧配置：
```bash
ros2 launch pb_option1_bringup sim_gz.launch.py mode:=nav \
  rviz_config_file:=/home/l/bjx_dzy/ros2_ws/src/pb_option1_description/rviz/visualize_robot.rviz
```

#### 4. 当前验证状态
已经确认的内容：

- 当前默认 GZ Sim 的 `mode:=nav` 可以启动到 Nav2 active
- GZ Sim 分支中 `/scan`、`/odom`、`map -> base_footprint`、`odom -> base_footprint` 都可以拿到
- `navigate_to_pose` action server 可用，基本导航动作链已经打通
- 默认 world 已切到工作区根目录下的 `resource/worlds/rmuc_2025_world.sdf`
- 默认静态地图已经替换为基于 `resource/models/rmuc_2025/meshes/rmuc_2025.stl` 生成的比赛场地地图

#### 5. 当前已知限制
需要注意以下几点：

- 当前默认地图已经切到 `rmuc_2025` 静态地图，但 AMCL 初始位姿仍建议继续和默认出生点一起对齐
- `real.launch.py` 和 `joystick.launch.py` 目前仍是空文件，实车链路还没有补完
- `pb_option1_sim/launch/gazebo_with_objects.launch.py` 现在也已经转到 GZ Sim，不再走 Gazebo Classic
- GZ Sim 的 headless 路径在某些机器上可能崩溃；带 GUI 时可能正常

GZ Sim 这里要特别说明：

- 当 `gui:=true` 时，GZ 使用正常窗口渲染
- 当 `gui:=false` 时，会走 `--headless-rendering`
- 两条渲染路径对显卡驱动和 OpenGL / EGL 的要求不同，所以“同一台机器 GUI 能跑、headless 崩溃”是可能发生的

#### 6. 常用排查命令
如果怀疑导航没起来，优先检查：

```bash
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 topic echo /map --once
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo map base_footprint
ros2 action list
```

如果想确认 Nav2 节点是否 active：

```bash
ros2 service call /map_server/get_state lifecycle_msgs/srv/GetState "{}"
ros2 service call /controller_server/get_state lifecycle_msgs/srv/GetState "{}"
ros2 service call /planner_server/get_state lifecycle_msgs/srv/GetState "{}"
ros2 service call /bt_navigator/get_state lifecycle_msgs/srv/GetState "{}"
```

### 二、pb_option1_description
由于模型使用了特殊的 xmacro 文件，需要额外依赖。第一次在新环境里使用机器人模型时，建议先做下面这些准备。

#### 1. 安装依赖
```bash
sudo apt install git-lfs
pip install vcstool2
pip install xmacro
```

#### 2. 导入相关仓库
```bash
cd src/pb_option1_description
vcs import --recursive < dependencies.repos
mv joint_state_publisher rmoss_gz_resources sdformat_tools ..
```

### 三、pb_option1_navigation
当前导航部分已经具备以下内容：

- `slam.launch.py`：SLAM Toolbox 建图入口
- `localization.launch.py`：Map Server + AMCL 定位入口
- `nav2_bringup.launch.py`：Nav2 服务器入口
- `nav2_params.yaml`：已经补齐 DWB controller、Navfn planner 等 Humble 所需参数

当前导航约定：

- base frame 使用 `base_footprint`
- 雷达话题统一为 `/scan`
- 里程计话题统一为 `/odom`
- GZ Sim 会通过桥接和 frame normalizer 把原始话题整理成上述格式
- 当前默认静态地图来自 `rmuc_2025` 场地 mesh 投影，生成脚本在 [tools/generate_field_map.py](/home/l/bjx_dzy/ros2_ws/src/pb_option1_navigation/tools/generate_field_map.py)

当前限制：

- 静态地图已经换成 `rmuc_2025`，但默认 AMCL 初始位姿还没和当前 spawn 点完全收敛
- 因此目前更准确的状态是“比赛地图已接入，导航链也打通了”，但还需要继续做定位初值和导航参数收敛

### 四、pb_option1_vision
### 1、准备工作
####  依赖准备（在workspace下）
```sh
vcs import src < src/dependencies.repos
sudo apt install git-lfs
pip install vcstool2
pip install xmacro
```
#### 编译
```sh 
colcon build --symlink-install
``` 
##### 如崩溃用这个
```sh
colcon build --symlink-install --parallel-workers 3
```
### 2、启动(vision功能)
#### 启动识别(单跑视觉)
```sh
ros2 launch pb_option1_bringup sim_vision.launch.py mode:=detect
```
#### 启动视觉(和导航共行)
```sh
ros2 launch pb_option1_bringup sim_vision.launch.py use_existing_sim:=true mode:=detect
```
#### 启动跟随
```sh
ros2 launch pb_option1_bringup sim_vision.launch.py mode:=follow
```
#### 启动跟随(和导航共行)
```sh
ros2 launch pb_option1_bringup sim_vision.launch.py use_existing_sim:=true mode:=follow
```
##### 在另一终端中启动相机,如想看到识别结果（在rviz中加入topic/vision/annotated_image）
```sh
ros2 run image_tools cam2image --ros-args -p device_id:=0
```
##### 可以启动控制小车
```sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```


当前视觉部分仍建议单独调试，不建议和导航联调问题混在一起排查。
