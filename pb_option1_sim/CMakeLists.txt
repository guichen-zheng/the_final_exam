cmake_minimum_required(VERSION 3.8)
project(pb_option1_sim)

# 编译选项
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 必须的包
find_package(ament_cmake REQUIRED)
find_package(gazebo_ros REQUIRED)

# 安装 launch 文件夹（关键！）
install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY
  worlds/
  DESTINATION share/${PROJECT_NAME}/worlds
)

# 如果还有 models/、config/ 等文件夹，也同样加进来

ament_package()
