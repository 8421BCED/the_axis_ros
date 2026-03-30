#!/usr/bin/env python3
"""
ULTRA SMOOTH ROBOT CONTROLLER - FIXED VERSION
Fixed issues:
- Proper trajectory following
- No jitter at target positions
- Smooth acceleration/deceleration
- Single source of truth for joint states
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import os
import json

class SmoothRobotController(Node):
    def __init__(self):
        super().__init__('smooth_robot_controller')
        
        # Publishers
        self.joint_state_pub = self.create_publisher(
            JointState, 
            '/joint_states', 
            10
        )
        
        # Subscriber for trajectory commands
        self.trajectory_sub = self.create_subscription(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            self.trajectory_callback,
            10
        )
        
        # Robot state
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint', 
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        # Current state
        self.current_positions = np.array([0.0, -1.57, 1.57, 0.0, 0.0, 0.0], dtype=np.float64)
        self.current_velocities = np.zeros(6, dtype=np.float64)
        self.target_positions = self.current_positions.copy()
        
        # Smooth motion parameters - OPTIMIZED
        self.max_velocity = 0.8  # rad/s - slower for smoother motion
        self.max_acceleration = 0.5  # rad/s²
        self.position_tolerance = 0.001  # rad - very tight tolerance
        
        # Trajectory following
        self.current_trajectory = None
        self.trajectory_start_time = None
        self.trajectory_duration = 0.0
        
        # Timer for publishing (100 Hz for super smooth motion)
        self.timer = self.create_timer(0.01, self.update_and_publish)  # 100 Hz
        
        # Publish robot description once
        self.publish_robot_description()
        
        self.get_logger().info('🤖 SMOOTH ROBOT CONTROLLER READY')
        self.get_logger().info(f'   Max velocity: {self.max_velocity} rad/s')
        self.get_logger().info(f'   Update rate: 100 Hz')
        
    def publish_robot_description(self):
        """Publish URDF for visualization"""
        desc_pub = self.create_publisher(String, '/robot_description', 10)
        
        # Find URDF file
        urdf_paths = [
            '/home/sweet/ros2_examples_ws/install/ur5_description/share/ur5_description/urdf/ur5.urdf',
            '/home/sweet/ros2_examples_ws/src/ur5_description/urdf/ur5.urdf',
            os.path.expanduser('~/ros2_examples_ws/install/ur5_description/share/ur5_description/urdf/ur5.urdf'),
        ]
        
        urdf_content = None
        for path in urdf_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    urdf_content = f.read()
                self.get_logger().info(f'✅ Loaded URDF from {path}')
                break
        
        if urdf_content:
            msg = String()
            msg.data = urdf_content
            desc_pub.publish(msg)
            self.get_logger().info('📢 Published robot_description')
    
    def trajectory_callback(self, msg):
        """Handle incoming trajectory commands"""
        try:
            if not msg.points:
                return
                
            # Get the first point (simplified for now)
            point = msg.points[0]
            
            if len(point.positions) != 6:
                self.get_logger().warn(f'Expected 6 joints, got {len(point.positions)}')
                return
            
            # Set target positions
            self.target_positions = np.array(point.positions, dtype=np.float64)
            
            # Calculate duration
            duration = point.time_from_start.sec + point.time_from_start.nanosec / 1e9
            if duration <= 0:
                duration = 2.0  # default duration
            
            # Create smooth trajectory
            self.current_trajectory = {
                'start_pos': self.current_positions.copy(),
                'target_pos': self.target_positions.copy(),
                'duration': duration,
                'start_time': time.time()
            }
            
            self.get_logger().info(
                f'🎯 Moving to: {np.round(self.target_positions, 3).tolist()} '
                f'in {duration:.1f}s'
            )
            
        except Exception as e:
            self.get_logger().error(f'Trajectory error: {e}')
    
    def update_and_publish(self):
        """Main control loop - called at 100 Hz"""
        current_time = time.time()
        
        # Update position based on active trajectory
        if self.current_trajectory is not None:
            elapsed = current_time - self.current_trajectory['start_time']
            duration = self.current_trajectory['duration']
            
            if elapsed >= duration:
                # Trajectory complete - snap to target
                self.current_positions = self.current_trajectory['target_pos'].copy()
                self.current_velocities = np.zeros(6)
                self.current_trajectory = None
                self.get_logger().info('✅ Movement complete')
            else:
                # Cubic interpolation for smooth motion
                t = elapsed / duration  # normalized time [0, 1]
                
                # Cubic polynomial: p(t) = start + (target-start) * (3t² - 2t³)
                # This gives zero velocity at start and end
                s = 3 * t * t - 2 * t * t * t  # cubic easing
                
                start = self.current_trajectory['start_pos']
                target = self.current_trajectory['target_pos']
                
                # Position
                self.current_positions = start + (target - start) * s
                
                # Velocity (derivative of cubic)
                ds_dt = 6 * t - 6 * t * t  # derivative
                velocity = (target - start) * ds_dt / duration
                
                # Limit velocity
                velocity_magnitude = np.linalg.norm(velocity)
                if velocity_magnitude > self.max_velocity:
                    velocity = velocity * (self.max_velocity / velocity_magnitude)
                
                self.current_velocities = velocity
        
        # Publish joint states
        self.publish_joint_states()
    
    def publish_joint_states(self):
        """Publish current joint states"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.current_positions.tolist()
        msg.velocity = self.current_velocities.tolist()
        
        # Add small amount of effort if needed by controllers
        msg.effort = [0.0] * 6
        
        self.joint_state_pub.publish(msg)


# Flask API for external control
app = Flask(__name__)
CORS(app)
controller = None

@app.route('/')
def home():
    return jsonify({
        'status': 'ready',
        'controller': 'Smooth Robot Controller',
        'endpoints': {
            '/move': 'POST - Move robot to joint positions',
            '/state': 'GET - Get current robot state',
            '/stop': 'POST - Emergency stop'
        }
    })

@app.route('/move', methods=['POST'])
def move():
    try:
        data = request.json
        positions = data.get('positions', [])
        duration = float(data.get('duration', 2.0))
        
        if len(positions) != 6:
            return jsonify({'error': 'Need 6 joint positions'}), 400
        
        # Create trajectory message
        msg = JointTrajectory()
        msg.joint_names = controller.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in positions]
        point.time_from_start.sec = int(duration)
        point.time_from_start.nanosec = int((duration - int(duration)) * 1e9)
        msg.points.append(point)
        
        # Send to controller
        controller.trajectory_callback(msg)
        
        return jsonify({
            'status': 'moving',
            'target': positions,
            'duration': duration
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/state', methods=['GET'])
def state():
    if controller:
        return jsonify({
            'current_positions': controller.current_positions.tolist(),
            'target_positions': controller.target_positions.tolist(),
            'velocities': controller.current_velocities.tolist(),
            'is_moving': controller.current_trajectory is not None
        })
    return jsonify({'error': 'Controller not ready'}), 500

@app.route('/stop', methods=['POST'])
def stop():
    if controller:
        controller.current_trajectory = None
        controller.target_positions = controller.current_positions.copy()
        return jsonify({'status': 'stopped'})
    return jsonify({'error': 'Controller not ready'}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

def main():
    global controller
    
    rclpy.init()
    controller = SmoothRobotController()
    
    # Start Flask in separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print('\n' + '='*60)
    print('🤖 SMOOTH ROBOT CONTROLLER - ACTIVE')
    print('='*60)
    print('✅ Joint states publishing at 100 Hz')
    print('✅ Flask API: http://localhost:5001')
    print('✅ Subscribed to /joint_trajectory_controller/joint_trajectory')
    print('='*60 + '\n')
    
    # Run ROS2 spin
    rclpy.spin(controller)
    
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()