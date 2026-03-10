# 安装指南

## 第一步: 确保在正确位置

```bash
# 进入ROS 2工作空间的src目录
cd ~/ros2_ws/src

# 如果工作空间不存在,创建它
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

## 第二步: 解压包

```bash
# 解压tar.gz文件
tar -xzf /path/to/pb_option1_vision.tar.gz

# 或者直接复制文件夹
cp -r /path/to/pb_option1_vision .

# 验证目录结构
ls pb_option1_vision/
# 应该看到: src/ config/ launch/ models/ package.xml CMakeLists.txt
```

## 第三步: 安装Python依赖

```bash
pip install ultralytics opencv-python
```

## 第四步: 安装ROS 2依赖

```bash
sudo apt update
sudo apt install ros-$ROS_DISTRO-cv-bridge
```

## 第五步: 编译

```bash
cd ~/ros2_ws
colcon build --packages-select pb_option1_vision
```

如果编译成功,应该看到:
```
Summary: 1 package finished [X.Xs]
```

## 第六步: Source环境

```bash
source ~/ros2_ws/install/setup.bash
```

## 第七步: 验证安装

```bash
# 检查包是否被识别
ros2 pkg list | grep pb_option1_vision

# 应该输出: pb_option1_vision

# 检查可执行文件
ros2 pkg executables pb_option1_vision

# 应该输出:
# pb_option1_vision object_detector.py
# pb_option1_vision command_interpreter_node.py
# pb_option1_vision follow_behavior_node.py
```

## 常见问题

### Q: colcon build找不到包?

A: 检查:
1. 确保在 `~/ros2_ws/src/` 目录下有 `pb_option1_vision` 文件夹
2. 确保 `pb_option1_vision` 文件夹里有 `package.xml` 文件
3. 尝试重新编译: `cd ~/ros2_ws && colcon build --packages-select pb_option1_vision`

### Q: 提示"ignoring unknown package"?

A: 说明包不在正确位置。执行:
```bash
# 检查目录结构
ls -la ~/ros2_ws/src/

# 确保看到 pb_option1_vision 目录
```

### Q: 编译成功但运行launch文件失败?

A: 记得每次打开新终端都要source:
```bash
source ~/ros2_ws/install/setup.bash
# 或添加到 ~/.bashrc:
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

## 成功后运行测试

```bash
# 终端1: 启动相机
ros2 run image_tools cam2image --ros-args -p device_id:=0

# 终端2: 启动视觉系统
ros2 launch pb_option1_vision vision_and_follow.launch.py mode:=command
```

成功! 🎉
