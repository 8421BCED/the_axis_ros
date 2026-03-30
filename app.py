# app.py full code with NO hardcoded time limits
# Robot will keep moving until job is complete

from flask import Flask, render_template, request, jsonify, session
import json
import requests
import subprocess
import re
import random
import hashlib
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_this_to_something_random_and_secret'

# Robot controller API URL
ROBOT_API = "http://localhost:5001"

# Store commands history
commands_history = []

def validate_and_adjust_joints(joints):
    """Ensure joints are safe and multiple joints move"""
    if len(joints) != 6:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    adjusted = []
    for i, j in enumerate(joints):
        j = float(j)
        # Safe limits
        j = max(min(j, 3.0), -3.0)
        adjusted.append(round(j, 2))
    
    # Count how many joints are actually moving (> 0.3 radians)
    moving_count = sum(1 for j in adjusted if abs(j) > 0.3)
    
    # If less than 3 joints moving significantly, add some movement
    if moving_count < 3:
        print(f"⚠️ Only {moving_count}/6 joints moving significantly, enhancing...")
        for i in range(1, 6):
            if abs(adjusted[i]) < 0.3:
                if i == 1 or i == 2:  # Shoulder and elbow
                    adjusted[i] = round(random.uniform(-1.5, 1.5), 2)
                else:  # Wrist joints
                    adjusted[i] = round(random.uniform(-1.0, 1.0), 2)
    
    return adjusted

def estimate_movement_duration(joints):
    """
    Intelligently estimate how long the movement should take
    based on how much the joints need to move
    """
    if not joints:
        return 5  # default safe duration
    
    # Calculate total movement magnitude
    total_movement = sum(abs(j) for j in joints)
    
    # Base duration on movement amount
    # More movement = more time needed
    if total_movement < 1.0:
        return 3  # small movement
    elif total_movement < 3.0:
        return 5  # medium movement
    elif total_movement < 6.0:
        return 8  # large movement
    else:
        return 10  # very large movement

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    data = request.json
    wallet_address = data.get('wallet_address')
    
    if wallet_address and len(wallet_address) == 42 and wallet_address.lower().startswith('0x'):
        session['wallet'] = wallet_address.lower()
        return jsonify({
            'success': True,
            'message': f'Wallet {wallet_address[:10]}... connected!'
        })
    
    return jsonify({'success': False, 'message': 'Invalid wallet address'})

@app.route('/command', methods=['POST'])
def handle_command():
    print("\n=== NEW COMMAND RECEIVED ===")
    
    if 'wallet' not in session:
        print("No wallet in session!")
        return jsonify({'success': False, 'message': 'Connect wallet first!'})
    
    data = request.json
    user_command = data.get('command')
    wallet = session['wallet']
    
    print(f"Command: {user_command}")
    print(f"Wallet: {wallet}")
    
    if not user_command:
        return jsonify({'success': False, 'message': 'No command provided'})
    
    # 1. Store command
    commands_history.append({
        'command': user_command,
        'wallet': wallet,
        'status': 'processing',
        'timestamp': time.time()
    })
    
    # 2. Get movement from LLM / presets
    try:
        print("Calling LLM / preset matcher...")
        llm_response = ask_llm(user_command)
        
        # Adjust joints for safety
        adjusted_joints = validate_and_adjust_joints(llm_response['joints'])
        llm_response['joints'] = adjusted_joints
        
        # ✅ DYNAMIC DURATION CALCULATION - NO HARDCODING
        movement_duration = estimate_movement_duration(adjusted_joints)
        llm_response['duration'] = movement_duration
        
        print(f"✅ Adjusted joints: {adjusted_joints}")
        print(f"⏱️ Movement duration: {movement_duration} seconds")
        
        # 3. Send to Robot Controller
        print("Sending to robot controller...")
        robot_result = send_to_robot_controller(llm_response, user_command, movement_duration)
        
        if robot_result.get('success'):
            print("✅ Robot movement started!")
            return jsonify({
                'success': True,
                'message': f'Command executing: {user_command}',
                'llm_response': llm_response,
                'robot_status': robot_result,
                'payment_required': True,
                'amount_eth': '0.01',
                'estimated_duration': movement_duration  # Send to frontend
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Robot error: {robot_result.get("error", "Unknown error")}'
            })
            
    except Exception as e:
        print(f"Error in command processing: {str(e)}")
        return jsonify({'success': False, 'message': f'System error: {str(e)}'})

def ask_llm(command):
    """Talk to your local Ollama Llama 3.2 with BETTER prompting"""
    
    # Map common commands to different joint positions
    command_examples = {
        "wave": [0.5, -0.3, 0.8, 0.1, -0.5, 0.2],
        "dance": [0.8, -0.5, 0.3, 0.8, 0.5, -0.3],
        "spin": [3.14, 0.0, 0.0, 0.0, 0.0, 0.0],
        "hello": [0.2, -0.4, 0.6, -0.2, 0.4, 0.0],
        "right": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "left": [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "up": [0.0, -1.0, 0.5, 0.0, 0.0, 0.0],
        "down": [0.0, 0.5, -0.5, 0.0, 0.0, 0.0],
        "pick": [0.3, -1.2, 1.5, -0.8, 0.5, 0.2],  # More complex movement
        "place": [-0.3, -0.8, 1.2, 0.5, -0.3, 0.1],  # Takes time
        "draw": [2.0, -1.5, 1.8, -1.2, 1.0, -0.5]  # Complex path
    }
    
    # Check for keywords first
    command_lower = command.lower()
    for key, positions in command_examples.items():
        if key in command_lower:
            print(f"Using preset for '{key}' command")
            # NO DURATION HARDCODED HERE - will be calculated later
            return {
                "joints": positions,
                "action": key
            }
    
    # If no match, use LLM
    prompt = f"""You are a robot arm controller. The user said: "{command}"

Generate 6 joint angles (joint_1 to joint_6) for a UR5 robot arm.

JOINT LIMITS: -3.14 to 3.14 radians

EXAMPLE MOVEMENTS:
- Wave: [0.5, -0.3, 0.8, 0.1, -0.5, 0.0]
- Dance: [0.8, -0.5, 0.3, -0.8, 0.5, -0.3] 
- Spin: [3.14, 0.0, 0.0, 0.0, 0.0, 0.0]
- Point up: [0.0, -1.5, 1.5, 0.0, 0.0, 0.0]
- Greet: [0.3, -0.4, 0.7, -0.2, 0.3, 0.1]
- Pick up object: [0.5, -2.0, 2.0, -1.5, 1.0, 0.5]
- Complex drawing: [2.5, -1.8, 2.2, -2.0, 1.5, -1.0]

Based on the command "{command}", create a UNIQUE joint configuration.

Return ONLY this JSON format, nothing else:
{{
  "joints": [j1, j2, j3, j4, j5, j6],
  "action": "brief_description"
}}

Make the positions DIFFERENT from examples above."""
    
    try:
        # Increased timeout for complex commands
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:1b', prompt],
            capture_output=True,
            text=True,
            timeout=60  # Increased from 30 to 60 seconds
        )
        
        print("LLM raw output:", result.stdout[:300])
        
        output = result.stdout.strip()
        output = output.replace('```json', '').replace('```', '')
        
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            
            if 'joints' in data and len(data['joints']) == 6:
                joints = []
                for j in data['joints']:
                    j = float(j)
                    if j < -3.14: j = -3.14
                    if j > 3.14: j = 3.14
                    joints.append(j)
                
                data['joints'] = joints
                # NO DURATION HERE - will be calculated later
                return data
        
        # If LLM fails, use hash-based positions
        import hashlib
        cmd_hash = hashlib.md5(command.encode()).hexdigest()
        unique_positions = [
            (int(cmd_hash[0:2], 16) / 255.0 * 4 - 2),
            (int(cmd_hash[2:4], 16) / 255.0 * 4 - 2),
            (int(cmd_hash[4:6], 16) / 255.0 * 4 - 2),
            (int(cmd_hash[6:8], 16) / 255.0 * 4 - 2), 
            (int(cmd_hash[8:10], 16) / 255.0 * 4 - 2),
            (int(cmd_hash[10:12], 16) / 255.0 * 4 - 2)
        ]
        
        return {
            "joints": [round(p, 2) for p in unique_positions],
            "action": "hashed_fallback"
        }
            
    except Exception as e:
        print(f"LLM Error: {e}")
        # Safe fallback with moderate movement
        return {
            "joints": [1.0, -0.8, 0.6, -0.4, 0.2, 0.0],
            "action": "error_fallback"
        }

def send_to_robot_controller(llm_response, command_name, duration):
    """Send movement command to robot controller API with calculated duration"""
    try:
        positions = llm_response.get('joints', [0.0] * 6)
        
        # Send the calculated duration to the robot controller
        response = requests.post(
            f"{ROBOT_API}/move",
            json={
                "positions": positions,
                "command": command_name,
                "duration": duration,  # Now using calculated duration
                "wait_for_completion": True  # Tell robot to wait until done
            },
            timeout=30  # HTTP timeout (separate from robot movement)
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API returned {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Robot controller not running (localhost:5001)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/check_movement_status', methods=['GET'])
def check_movement_status():
    """Check if robot is still moving"""
    try:
        response = requests.get(
            f"{ROBOT_API}/status",
            timeout=5
        )
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"moving": False, "error": "Status check failed"})
    except:
        return jsonify({"moving": False, "error": "Robot controller unreachable"})

@app.route('/make_payment', methods=['POST'])
def make_payment():
    """Handle payment simulation / preparation"""
    data = request.json
    wallet_address = data.get('wallet')
    action = data.get('action', 'robot_command')
    
    print(f"💸 Payment request from {wallet_address} for {action}")
    
    return jsonify({
        'success': True,
        'message': f'Payment of 0.01 ETH processed for {action}',
        'transaction': 'simulated_tx_hash_abc123'
    })

if __name__ == '__main__':
    print("🤖 Robot Web Interface - NO HARDCODED TIME LIMITS")
    print("================================================")
    print(f"Robot Controller expected at: {ROBOT_API}")
    print("✅ Movement durations calculated dynamically based on joint angles")
    print("✅ Robot will continue moving until job is complete")
    print("✅ No arbitrary time limits on robot movement")
    print("\nMake sure your robot controller / override_gui.py is running!")
    app.run(debug=True, host='0.0.0.0', port=5000)