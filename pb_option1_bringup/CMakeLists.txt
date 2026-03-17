cmake_minimum_required(VERSION 3.8)
project(pb_option1_bringup)

# C++ 编译选项（可选，保持默认就好）
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 必须的构建工具
find_package(ament_cmake REQUIRED)

# 运行时依赖：这些包在 launch 文件中会被启动，所以在这里声明比较好
# 实际使用时 ROS 2 会检查它们是否存在
find_package(gazebo_ros REQUIRED)             # 启动 Gazebo
find_package(robot_state_publisher REQUIRED)  # 发布 robot_description 和 TF
find_package(usb_cam REQUIRED)                # 真实摄像头节点

# 你的自定义包（模型和视觉）
# find_package(pb_option1_description REQUIRED)
# find_package(pb_option1_vision REQUIRED)

# 安装 launch 文件夹（核心功能）
install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY
  config/
  DESTINATION share/${PROJECT_NAME}/config
)
# install(DIRECTORY rviz/
#   DESTINATION share/${PROJECT_NAME}/rviz
# )
# install(DIRECTORY params/
#   DESTINATION share/${PROJECT_NAME}/params
# )
# install(DIRECTORY worlds/
#   DESTINATION share/${PROJECT_NAME}/worlds
# )

# 导出包信息（必须）
ament_package()
