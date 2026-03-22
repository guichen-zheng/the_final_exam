# pb_option1_vision

基于YOLO的物体检测与跟随系统

## 功能

1. **物体检测**: 使用YOLOv8检测水杯、苹果、香蕉
2. **命令控制**: 根据物体执行动作
   - 水杯 → 直行
   - 苹果 → 左转
   - 香蕉 → 右转
3. **跟随模式**: 机器人跟随检测到的物体

## 快速开始

### 1. 安装依赖

```bash
pip install ultralytics opencv-python
sudo apt install ros-$ROS_DISTRO-cv-bridge
```

### 2. 编译

```bash
cd ~/ros2_ws
colcon build --packages-select pb_option1_vision
source install/setup.bash
```

### 3. 运行

```bash
# 终端1: 启动相机
ros2 run image_tools cam2image --ros-args -p device_id:=0

# 终端2: 启动视觉系统(命令模式)
ros2 launch pb_option1_vision vision_and_follow.launch.py mode:=command

# 或启动跟随模式
ros2 launch pb_option1_vision vision_and_follow.launch.py mode:=follow
```

## 项目结构

```
pb_option1_vision/
├── src/
│   ├── object_detector.py            # YOLO检测
│   ├── command_interpreter_node.py   # 物体→动作映射
│   └── follow_behavior_node.py       # 跟随控制
├── config/
│   ├── detector_params.yaml         # 检测参数
│   └── follow_params.yaml           # 跟随参数
├── launch/
│   └── vision_and_follow.launch.py  # 启动文件
└── models/                          # YOLO模型目录
```

## 话题

**发布:**
- `/vision/detected_object` - 检测到的物体类型
- `/vision/object_position` - 物体位置
- `/vision/annotated_image` - 标注图像
- `/cmd_vel` - 速度命令

**订阅:**
- `/camera/image_raw` - 相机图像

## 配置

### 检测参数 (`config/detector_params.yaml`)

```yaml
model_path: "yolov8n.pt"
confidence_threshold: 0.5
device: "cpu"  # 改为"cuda"启用GPU
```

### 跟随参数 (`config/follow_params.yaml`)

```yaml
linear_speed: 0.3
angular_speed: 0.5
```

## 故障排除

**Q: 检测不到物体?**
A: 降低confidence_threshold到0.3

**Q: 检测速度慢?**
A: 使用GPU: `device: "cuda"`

**Q: 机器人不动?**
A: 检查/cmd_vel话题: `ros2 topic echo /cmd_vel`
