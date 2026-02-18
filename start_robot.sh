#!/bin/bash
echo "🤖 Starting UR5 Robot (No GUI Interference)"

cd ~/ros2_examples_ws
source install/setup.bash

# Find the actual files
URDF_PATH=""
RVIZ_PATH=""

# Try multiple possible locations
POSSIBLE_URDFS=(
    "install/ur5_description/share/ur5_description/urdf/ur5.urdf"
    "src/ur5_description/urdf/ur5.urdf"
    "share/ur5_description/urdf/ur5.urdf"
)

POSSIBLE_RVIZ=(
    "install/ur5_description/share/ur5_description/launch/display.rviz"
    "src/ur5_description/launch/display.rviz"
    "share/ur5_description/launch/display.rviz"
)

for urdf in "${POSSIBLE_URDFS[@]}"; do
    if [ -f "$urdf" ]; then
        URDF_PATH="$urdf"
        break
    fi
done

for rviz in "${POSSIBLE_RVIZ[@]}"; do
    if [ -f "$rviz" ]; then
        RVIZ_PATH="$rviz"
        break
    fi
done

if [ -z "$URDF_PATH" ] || [ -z "$RVIZ_PATH" ]; then
    echo "❌ Could not find required files!"
    echo "Looking for:"
    echo "  URDF: ${POSSIBLE_URDFS[*]}"
    echo "  RViz: ${POSSIBLE_RVIZ[*]}"
    exit 1
fi

echo "✅ Found URDF: $URDF_PATH"
echo "✅ Found RViz config: $RVIZ_PATH"

# Start robot_state_publisher
echo "🚀 Starting robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args \
    -p robot_description:="$(cat $URDF_PATH)" &
RSP_PID=$!

echo "Robot State Publisher PID: $RSP_PID"

# Wait
sleep 3

# Start RViz
echo "🖥️ Starting RViz..."
ros2 run rviz2 rviz2 -d "$RVIZ_PATH" &
RVIZ_PID=$!

echo "RViz PID: $RVIZ_PID"

echo ""
echo "=========================================="
echo "🤖 ROBOT LAUNCHED SUCCESSFULLY!"
echo "=========================================="
echo "To stop:"
echo "1. Close RViz window"
echo "2. Run: kill $RSP_PID"
echo "=========================================="

# Keep script running
wait