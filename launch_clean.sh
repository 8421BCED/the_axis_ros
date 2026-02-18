#!/bin/bash
echo "🚀 Launching robot WITHOUT joint_state_publisher_gui..."

# Find the launch file
LAUNCH_FILE=$(find ~/ros2_examples_ws -name "display_robot.launch.py" -type f | head -1)

if [ -z "$LAUNCH_FILE" ]; then
    echo "❌ Could not find launch file!"
    exit 1
fi

echo "📄 Using launch file: $LAUNCH_FILE"

# Launch with substitution to remove GUI
cd ~/ros2_examples_ws
source install/setup.bash

# Create a temporary modified launch file
TEMP_LAUNCH="/tmp/robot_no_gui.launch.py"

cat > "$TEMP_LAUNCH" << 'EOF'
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # Get package directory
    ur5_description_dir = get_package_share_directory('ur5_description')
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': ''}],
        arguments=['robot_description:=/robot_description']
    )
    
    # RViz2
    rviz_config_file = os.path.join(ur5_description_dir, 'launch', 'display.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )
    
    return LaunchDescription([
        robot_state_publisher,
        rviz,
    ])
EOF

echo "✅ Created launch file without GUI"
echo "🤖 Starting robot..."

# Launch the modified file
ros2 launch "$TEMP_LAUNCH"