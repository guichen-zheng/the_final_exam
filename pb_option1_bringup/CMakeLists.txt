cmake_minimum_required(VERSION 3.8)
project(pb_option1_bringup)

# C++ 编译选项（可选，保持默认就好）
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 必须的构建工具
find_package(ament_cmake REQUIRED)

# 运行时依赖：这些包会在 launch 阶段被调用，不需要在 CMake 配置阶段解析
find_package(robot_state_publisher REQUIRED)
find_package(usb_cam REQUIRED)

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
