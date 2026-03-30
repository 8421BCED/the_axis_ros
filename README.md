# UR5 Robot Commander

**Live Demo:** https://[your-username].github.io/[repo-name]/

![Screenshot](static/screen.png)

## Features
- Web3 wallet integration
- Real-time robot control
- Command execution with ETH payments

## Quick Start
```bash
./start_robot.sh

text


Then put your full HTML in `docs/index.html` and enable GitHub Pages.

### Option 2: Professional Markdown README
Here's what you can actually use (will work perfectly):

```markdown
# UR5 Robot Commander | Tsion Dynamics

<p align="center">
  <img src="static/tsion.jpeg" width="120">
</p>

<p align="center">
  <img src="static/screen.png" width="300">
  <img src="static/image.png" width="300">
</p>

<p align="center">
  <video src="static/cast.mp4" controls width="600"></video>
</p>

---

## Architecture

┌─────────────┐ ┌──────────┐ ┌─────────┐
│ Web UI │────▶│ Web3 │────▶│ ROS2 │
│ (React) │ │ Wallet │ │ Bridge │
└─────────────┘ └──────────┘ └─────────┘
│
▼
┌─────────────┐
│ UR5 Robot │
└─────────────┘
text


## Wallet Connection

```python
from web3 import Web3

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_KEY'))
wallet = "0x..."  # Your wallet address

Available Commands
Command	Description	Cost (ETH)
dance	Dance routine	0.05
spin 360	Full rotation	0.03
grab x y z	Pick object	0.10
Robot Joint Control
yaml

joint_1 (Base):      ████████░░ 75%
joint_2 (Shoulder):  ██████░░░░ 60%
joint_3 (Elbow):     ██████████ 100%
joint_4 (Wrist 1):   ████░░░░░░ 40%
joint_5 (Wrist 2):   ███████░░░ 70%
joint_6 (Wrist 3):   ██████░░░░ 55%

Installation
bash

# Clone repository
git clone https://github.com/yourusername/ur5-commander

# Install dependencies
pip install -r requirements.txt

# Launch robot controller
./start_robot.sh

Files

    ros2_bridge.py - ROS2 communication layer

    smooth_robot_controller.py - Motion planning

    override_gui.py - UI controls

Technologies

    ROS2 Humble

    Python 3.8+

    Web3.py

    Ethereum Blockchain

Support
<p align="center"> Built by <strong>Tsion Dynamics</strong><br> Supported by Ethereum Foundation </p> `
