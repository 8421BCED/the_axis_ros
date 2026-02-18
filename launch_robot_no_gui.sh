#!/bin/bash
cd ~/ros2_examples_ws
source install/setup.bash

# Launch ONLY robot_state_publisher and rviz2 (NO joint_state_publisher_gui)
ros2 run robot_state_publisher robot_state_publisher &
sleep 2
ros2 run rviz2 rviz2 -d $(find . -name "display.rviz" | head -1) &
echo "✅ Robot launched WITHOUT GUI interference"
echo "🤖 Now fully controlled by our smooth controller"