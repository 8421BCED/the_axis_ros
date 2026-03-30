# UR5 Robot Commander | Tsion Dynamics

<p align="center">
  <img src="static/tsion.jpeg" width="120">
</p>

<p align="center">
  <img src="static/screen.png" width="45%">
  <img src="static/image.png" width="45%">
</p>

<p align="center">
  <video src="static/cast.mp4" controls width="80%"></video>
</p>

---

## Architecture

┌─────────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐
│ Web UI │────▶│ Web3 │────▶│ ROS2 │────▶│ UR5 │
│ (Flask) │ │ Wallet │ │ Bridge │ │ Robot │
└─────────────┘ └──────────┘ └─────────┘ └─────────────┘
text


## Features

- Web3 wallet integration with Ethereum payments
- Real-time UR5 robot control via ROS2
- Command execution with smart contract verification
- Smooth trajectory planning
- Interactive GUI override

## Quick Start

```bash
# Launch the robot controller
./start_robot.sh

# Or launch without GUI
./launch_robot_no_gui.sh

# Clean launch
./launch_clean.sh

Wallet Connection

The system uses Ethereum smart contracts for payment verification:
python

# Smart contract at: RobotPayment.sol
# Deployed address: See contract_address.txt

from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

Available Commands
Command	Description	Cost (ETH)
dance	Execute dance routine	0.05
spin 360	Full rotation	0.03
grab X Y Z	Pick object at coordinates	0.10
wave	Perform waving motion	0.02
reset	Return to home position	0.00
Robot Joint Control
text

Joint 1 (Base):      ████████░░ 75%
Joint 2 (Shoulder):  ██████░░░░ 60%
Joint 3 (Elbow):     ██████████ 100%
Joint 4 (Wrist 1):   ████░░░░░░ 40%
Joint 5 (Wrist 2):   ███████░░░ 70%
Joint 6 (Wrist 3):   ██████░░░░ 55%

Project Structure
text

.
├── app.py                      # Flask web application
├── ros2_bridge.py              # ROS2 communication layer
├── smooth_robot_controller.py  # Motion planning algorithms
├── override_gui.py             # Custom UI controls
├── RobotPayment.sol            # Ethereum smart contract
├── deploy_contract.py          # Contract deployment script
├── start_robot.sh              # Main launch script
├── static/                     # Images and media
│   ├── tsion.jpeg
│   ├── screen.png
│   ├── image.png
│   └── cast.mp4
├── templates/                  # HTML templates
└── ros_ws/                     # ROS2 workspace

Smart Contract Deployment
bash

# Deploy the payment contract
python3 deploy_contract.py

# Contract address saved to contract_address.txt

Requirements

    ROS2 Humble or Foxy

    Python 3.8+

    Ubuntu 20.04/22.04

    Ethereum client (Ganache or Geth)

    Web3.py

Files Overview
File	Purpose
ros2_bridge.py	Bridges ROS2 topics with web interface
smooth_robot_controller.py	Implements smooth motion planning
override_gui.py	Custom GUI overrides for manual control
RobotPayment.sol	Solidity smart contract for ETH payments
app.py	Flask backend server
License

MIT License
<p align="center"> <strong>Built by Tsion Dynamics</strong><br> Supported by Ethereum Foundation </p><p align="center"> <a href="#">Documentation</a> • <a href="#">Issues</a> • <a href="#">Discord</a> </p> ```
