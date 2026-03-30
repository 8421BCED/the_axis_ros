# override_gui.py full code with fixes for idle jitter

#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
import time
import json
import threading
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

class UltraSmoothRobotController(Node):
    def __init__(self):
        super().__init__('ultra_smooth_robot_controller')
        
        # Publisher for joint states
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        
        # Optional: publish robot_description (helps RViz / visualization)
        self.desc_pub = self.create_publisher(String, '/robot_description', 10)
        self.publish_robot_description()
        
        # Control variables
        self.target_positions = [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]  # Initial home pose
        self.current_positions = self.target_positions.copy()
        self.current_velocities = [0.0] * 6
        self.is_active = True
        
        # Tuned parameters for faster + smooth movement
        self.max_speed = 1.10  # rad/s - faster
        self.acceleration = 0.45  # quicker ramp-up
        self.smoothing = 0.20  # responsive but controlled
        self.deadzone = 0.005  # Increased for stability
        
        self.movement_queue = []
        self.current_movement = None
        
        # Timer: 50 Hz publishing
        self.timer = self.create_timer(0.02, self.publish_continuous_states)
        
        self.last_publish_time = time.time()
        
        print("=" * 70)
        print("🤖 ULTRA SMOOTH + FASTER ROBOT CONTROLLER")
        print(f" max_speed : {self.max_speed:.2f} rad/s")
        print(f" acceleration : {self.acceleration:.2f}")
        print(f" smoothing : {self.smoothing:.2f}")
        print(" Publishing @ 50 Hz")
        print("=" * 70)
        
        self.get_logger().info("Controller active - continuously publishing joint states")
    
    def publish_robot_description(self):
        """Publish URDF for visualization tools (RViz, etc.)"""
        urdf_paths = [
            '/home/sweet/ros2_examples_ws/install/ur5_description/share/ur5_description/urdf/ur5.urdf',
            '/home/sweet/ros2_examples_ws/src/ur5_description/urdf/ur5.urdf',
            os.path.expanduser('~/ros2_examples_ws/install/ur5_description/share/ur5_description/urdf/ur5.urdf'),
        ]
        urdf_content = ""
        for path in urdf_paths:
            try:
                with open(path, 'r') as f:
                    urdf_content = f.read()
                print(f"✅ Loaded real URDF from: {path}")
                break
            except:
                continue
        
        if not urdf_content:
            print("⚠️ No URDF found - using minimal fallback")
            urdf_content = """<?xml version="1.0"?>
<robot name="ur5">
  <link name="base_link"/>
  <joint name="joint_1" type="revolute">
    <parent link="base_link"/>
    <child link="shoulder_link"/>
    <axis xyz="0 0 1"/>
  </joint>
  <!-- minimal placeholder - add real URDF path above for full model -->
</robot>"""
        
        msg = String()
        msg.data = urdf_content
        self.desc_pub.publish(msg)
        print("📢 robot_description published")
    
    def publish_continuous_states(self):
        """50 Hz continuous publishing loop"""
        current_time = time.time()
        dt = current_time - self.last_publish_time
        self.last_publish_time = current_time
        
        self.update_movement()
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'world'
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        msg.position = [round(p, 6) for p in self.current_positions]
        msg.velocity = [round(v, 6) for v in self.current_velocities]
        
        self.publisher.publish(msg)
        
        # Low-frequency logging (every ~2 seconds)
        if int(current_time) % 2 == 0:
            moving_joints = sum(1 for i in range(6) if abs(self.target_positions[i] - self.current_positions[i]) > 0.01)
            if moving_joints > 0:
                self.get_logger().info(f"Moving {moving_joints} joints | Queue: {len(self.movement_queue)}")
    
    def update_movement(self):
        all_reached = True
        for i in range(6):
            error = self.target_positions[i] - self.current_positions[i]
            abs_error = abs(error)
            
            if abs_error > self.deadzone:
                all_reached = False
                # Proportional + limited velocity
                desired_velocity = error * self.smoothing
                desired_velocity = max(min(desired_velocity, self.max_speed), -self.max_speed)
                
                # Accelerate smoothly
                vel_error = desired_velocity - self.current_velocities[i]
                acc = self.acceleration if abs_error > 0.1 else self.acceleration * 0.4
                self.current_velocities[i] += vel_error * acc * 0.02  # dt = timer period
                
                # Position update
                self.current_positions[i] += self.current_velocities[i] * 0.02
                
                # Prevent overshoot
                if (error > 0 and self.current_positions[i] > self.target_positions[i]) or \
                   (error < 0 and self.current_positions[i] < self.target_positions[i]):
                    self.current_positions[i] = self.target_positions[i]
                    self.current_velocities[i] = 0.0
            else:
                # Close enough → snap + zero velocity
                self.current_positions[i] = self.target_positions[i]
                self.current_velocities[i] = 0.0
        
        if all_reached and self.current_movement:
            print(f"✅ Completed: {self.current_movement.get('name', 'unnamed')}")
            self.current_movement = None
            if self.movement_queue:
                self.start_next_movement()
    
    def start_next_movement(self):
        if self.movement_queue:
            self.current_movement = self.movement_queue.pop(0)
            self.target_positions = self.current_movement['positions'].copy()
            self.current_velocities = [0.0] * 6
            print(f"🎬 Starting: {self.current_movement['name']}")
            print(f" Target: {[round(x, 3) for x in self.target_positions]}")
            duration = self.current_movement.get('duration', 10)
            threading.Timer(duration, self.check_movement_completion).start()
    
    def check_movement_completion(self):
        if self.current_movement:
            close_enough = all(abs(self.target_positions[i] - self.current_positions[i]) <= 0.05 for i in range(6))
            if close_enough:
                self.current_movement = None
                if self.movement_queue:
                    self.start_next_movement()
    
    def add_movement(self, positions, command_name="movement", duration=3):
        movement = {
            'positions': [float(p) for p in positions],
            'name': command_name,
            'duration': duration,
            'added_time': time.time()
        }
        print(f"\n📥 New command: {command_name}")
        print(f" Positions: {[round(x, 3) for x in positions]}")
        
        self.movement_queue.append(movement)
        
        if not self.current_movement and len(self.movement_queue) == 1:
            self.start_next_movement()
        
        queue_pos = len(self.movement_queue) - 1 if self.current_movement else 0
        return {
            "status": "started" if queue_pos == 0 else "queued",
            "command": command_name,
            "queue_position": queue_pos
        }
    
    def emergency_stop(self):
        self.movement_queue.clear()
        self.current_movement = None
        self.target_positions = self.current_positions.copy()
        print("🛑 EMERGENCY STOP - All movements cleared")
        return {"status": "stopped"}
    
    def get_current_state(self):
        errors = [round(abs(self.target_positions[i] - self.current_positions[i]), 4) for i in range(6)]
        moving_joints = sum(1 for err in errors if err > 0.01)
        return {
            "current_positions": [round(p, 3) for p in self.current_positions],
            "target_positions": [round(p, 3) for p in self.target_positions],
            "errors": errors,
            "velocities": [round(v, 3) for v in self.current_velocities],
            "moving_joints": moving_joints,
            "current_movement": self.current_movement['name'] if self.current_movement else None,
            "queue_length": len(self.movement_queue),
            "is_active": self.is_active
        }

# Flask API setup
app = Flask(__name__)
CORS(app)
controller = None

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "service": "Ultra Smooth Robot Controller",
        "mode": "100% CONTROL - NO GUI INTERFERENCE",
        "endpoints": {
            "/move": "POST - Add movement (positions, command, duration)",
            "/state": "GET - Current state",
            "/stop": "POST - Emergency stop",
            "/queue": "GET - Movement queue"
        }
    })

@app.route('/move', methods=['POST'])
def move_robot():
    try:
        data = request.json
        if not data or 'positions' not in data:
            return jsonify({"error": "Missing 'positions' array"}), 400
        
        positions = data.get('positions')
        command_name = data.get('command', 'unnamed')
        duration = max(1.0, min(float(data.get('duration', 3)), 10))
        
        if len(positions) != 6:
            return jsonify({"error": "Need exactly 6 joint positions"}), 400
        
        
        valid_positions = []
        for i, pos in enumerate(positions):
            try:
                p = float(pos)
                p = max(min(p, 3.0), -3.0)
                valid_positions.append(p)
            except:
                return jsonify({"error": f"Invalid position for joint {i+1}: {pos}"}), 400
        
        if controller:
            result = controller.add_movement(valid_positions, command_name, duration)
            return jsonify(result)
        else:
            return jsonify({"error": "Controller not ready"}), 500
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/state', methods=['GET'])
def get_state():
    if controller:
        return jsonify(controller.get_current_state())
    return jsonify({"error": "Controller not ready"}), 500

@app.route('/stop', methods=['POST'])
def emergency_stop():
    if controller:
        result = controller.emergency_stop()
        return jsonify(result)
    return jsonify({"error": "Controller not ready"}), 500

@app.route('/queue', methods=['GET'])
def get_queue():
    if controller:
        return jsonify({
            "queue": [m['name'] for m in controller.movement_queue],
            "length": len(controller.movement_queue),
            "current": controller.current_movement['name'] if controller.current_movement else None
        })
    return jsonify({"error": "Controller not ready"}), 500

def start_flask():
    print("🌐 Starting Flask API on http://0.0.0.0:5001 ...")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

def main():
    global controller
    print("🚀 Initializing ULTRA SMOOTH Robot Controller...")
    rclpy.init()
    
    try:
        controller = UltraSmoothRobotController()
        flask_thread = threading.Thread(target=start_flask, daemon=True)
        flask_thread.start()
        
        print("\n" + "="*70)
        print("🎯 SYSTEM READY!")
        print("✅ Robot Controller: ACTIVE (100% control)")
        print("✅ Flask API: http://localhost:5001")
        print("="*70 + "\n")
        
        def gentle_test():
            time.sleep(2)
            if controller:
                print("🧪 Running gentle test movement...")
                controller.add_movement(
                    [0.5, -0.3, 0.4, -0.2, 0.3, 0.1],
                    "gentle_test",
                    2
                )
        
        test_thread = threading.Thread(target=gentle_test, daemon=True)
        test_thread.start()
        
        rclpy.spin(controller)
    
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        if controller:
            controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()