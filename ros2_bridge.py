#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import json
import time

class LLMController(Node):
    def __init__(self):
        super().__init__('llm_controller')
        
        # Publisher for joint commands
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # UR5 joint names
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        self.get_logger().info('🤖 LLM Controller ready!')
    
    def execute_movement(self, joint_angles, duration=3.0):
        """Move robot to specified joint angles"""
        try:
            # Create trajectory
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names
            
            # Create point
            point = JointTrajectoryPoint()
            point.positions = joint_angles
            point.time_from_start.sec = int(duration)
            point.time_from_start.nanosec = int((duration - int(duration)) * 1e9)
            
            trajectory.points.append(point)
            
            # Publish
            self.publisher.publish(trajectory)
            self.get_logger().info(f'Moving robot to: {joint_angles}')
            
            return True
            
        except Exception as e:
            self.get_logger().error(f'Movement failed: {e}')
            return False

# Simple test function
def test_robot_movement():
    rclpy.init()
    controller = LLMController()
    
    # Test wave motion
    wave_angles = [0.5, -0.3, 0.8, 0.1, -0.5, 0.2]
    
    print("Testing robot movement in 3 seconds...")
    time.sleep(3)
    
    success = controller.execute_movement(wave_angles, 2.0)
    
    if success:
        print("✅ Robot should be moving! Check Rviz!")
    else:
        print("❌ Movement failed")
    
    time.sleep(3)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    test_robot_movement()