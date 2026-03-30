<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif; }
    body { background: #f4f7fc; min-height: 100vh; display: flex; justify-content: center; padding: 24px; margin: 0; }
    .container { width: 100%; max-width: 900px; background: #ffffff; border-radius: 24px; box-shadow: 0 20px 40px -12px rgba(0,20,40,0.25); padding: 32px; border: 1px solid #eaedf2; }
    
    /* Header */
    .header { text-align: center; margin-bottom: 28px; }
    .header img { width: 120px; display: block; margin: 0 auto; border-radius: 12px; }
    .header h1 { font-size: 2rem; margin-top: 12px; color: #1a2639; letter-spacing: -0.02em; font-weight: 600; }
    .header h1 span { font-size: 0.8rem; background: #1a2639; color: white; padding: 4px 12px; border-radius: 40px; font-weight: 400; }
    
    /* Sponsor */
    .sponsor { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
    .sponsor img { height: 48px; }
    
    /* Media Cards */
    .media-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .media-card { background: #f9fbfd; border-radius: 18px; padding: 16px; border: 1px solid #e2e9f2; text-align: center; }
    .media-card img, .media-card video { width: 100%; border-radius: 12px; max-height: 200px; object-fit: cover; }
    .media-card video { max-height: 200px; }
    
    /* Wallet Section */
    .wallet-section { background: #f9fbfd; border-radius: 18px; padding: 20px 24px; margin: 24px 0 28px; border: 1px solid #e2e9f2; }
    .wallet-section h3 { margin-bottom: 16px; color: #1e2b3c; font-weight: 500; }
    #walletInfo p { display: flex; align-items: center; gap: 12px; font-size: 0.95rem; color: #2d3f56; flex-wrap: wrap; }
    #walletAddress, #walletBalance { border-radius: 40px; padding: 8px 16px; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.9rem; }
    #walletAddress { background: white; border: 1px solid #d0ddee; color: #0b1c2e; }
    #walletBalance { background: #e8f0fe; border: 1px solid #b9d1f0; font-weight: 600; color: #1e3e6e; }
    #connectWallet input { width: 100%; padding: 14px 18px; border-radius: 14px; border: 1px solid #cfddee; margin-bottom: 12px; font-size: 1rem; }
    #connectWallet input:focus { outline: none; border-color: #3a7bd5; box-shadow: 0 0 0 3px rgba(58,123,213,0.08); }
    
    /* Buttons */
    button { border: none; padding: 10px 22px; font-size: 0.95rem; font-weight: 500; border-radius: 40px; cursor: pointer; transition: 0.15s; margin: 0 6px 6px 0; box-shadow: 0 2px 6px rgba(0,20,40,0.08); }
    button.primary { background: #1e2f4a; color: white; }
    button.primary:hover { background: #253c5c; transform: translateY(-1px); }
    button.secondary { background: #ffffff; color: #1e2f4a; border: 1px solid #c8d5e6; }
    button.secondary:hover { background: #f2f7ff; transform: translateY(-1px); }
    
    .input-group { margin: 24px 0; }
    #commandInput { width: 100%; padding: 16px 20px; font-size: 1rem; border: 1px solid #dae2ed; border-radius: 18px; margin-bottom: 16px; }
    #commandInput:focus { border-color: #3a7bd5; outline: none; box-shadow: 0 0 0 4px rgba(58,123,213,0.08); }
    
    /* Alerts */
    .alert { padding: 16px 22px; border-radius: 60px; margin: 20px 0; display: none; font-weight: 500; font-size: 0.95rem; }
    .alert.success { background: #f1f9f0; color: #1d5a3e; border: 1px solid #a8d5b5; }
    .alert.error { background: #fee9e7; color: #a12b2b; border: 1px solid #fbb4b4; }
    
    /* Payment */
    .payment-section { background: #f2f7ff; border-radius: 20px; padding: 20px 26px; margin: 28px 0 20px; display: none; border: 1px solid #bfd6f0; }
    .payment-section h3 { margin-top: 0; color: #1e3e6e; font-weight: 500; }
    .payment-section p { margin: 12px 0; color: #1a2f48; }
    .payment-section strong { padding: 4px 12px; border-radius: 30px; border: 1px solid #b9d1f0; background: #ffffffb0; font-weight: 600; }
    
    /* Command History */
    .command-history { margin: 32px 0 10px; background: #fafcff; border-radius: 20px; padding: 12px; }
    .command-item { background: #ffffff; padding: 14px 18px; margin: 10px 0; border-radius: 16px; border: 1px solid #e6ecf5; display: flex; justify-content: space-between; flex-wrap: wrap; }
    .status { font-size: 0.8rem; font-weight: 500; padding: 5px 12px; border-radius: 40px; min-width: 85px; text-align: center; }
    .status.done { background: #e2f3e4; color: #166b3b; border: 1px solid #b2e0ba; }
    .status.error { background: #fde4e1; color: #bb2d2d; border: 1px solid #fbc1bc; }
    .status.paid { background: #ece3ff; color: #583c9e; border: 1px solid #cbb8ff; }
    
    /* Joint Visualization */
    .joint-visualization { margin: 32px 0 8px; background: #f9fcff; border-radius: 20px; padding: 22px; border: 1px solid #e2ecfb; }
    .joint { margin: 14px 0; }
    .joint-label { font-size: 0.8rem; font-weight: 600; color: #3e5670; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.3px; }
    .joint-bar { height: 24px; background: #e2e9f2; border-radius: 40px; overflow: hidden; }
    .joint-fill { height: 100%; color: white; text-align: center; font-size: 0.75rem; font-weight: 500; line-height: 24px; transition: width 0.5s ease; background: #3a6ea5; }
    
    .footer { text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid #eaedf2; color: #6b7c93; font-size: 0.85rem; }
    a { color: #1e2f4a; text-decoration: none; }
    a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">

    <!-- Header with Tsion Brand -->
    <div class="header">
        <img src="/home/sweet/myhead/static/tsion.jpeg" alt="Tsion Dynamics">
        <h1>UR5 <span>Controller</span></h1>
    </div>

    <!-- Media Gallery -->
    <div class="media-grid">
        <div class="media-card">
            <img src="/home/sweet/myhead/static/screen.png" alt="Robot Interface">
        </div>
        <div class="media-card">
            <img src="/home/sweet/myhead/static/image.png" alt="Robot Demo">
        </div>
        <div class="media-card">
            <video src="/home/sweet/myhead/static/cast.mp4" controls autoplay loop muted></video>
        </div>
    </div>

    <!-- Ethereum Foundation Support -->
    <div class="sponsor">
        <img src="/home/sweet/myhead/static/ethereum.png" alt="Ethereum Foundation" onerror="this.style.display='none'">
        <span style="font-size:0.9rem; color:#2c3e50;">Supported by Ethereum Foundation</span>
    </div>

    <!-- Wallet Section -->
    <div class="wallet-section">
        <h3>Wallet Connection</h3>
        <div id="walletInfo" style="display:none;">
            <p>
                Connected: <strong id="walletAddress"></strong>
                Balance: <span id="walletBalance">0 ETH</span>
                <button onclick="disconnectWallet()" class="secondary">Disconnect</button>
            </p>
        </div>
        <div id="connectWallet">
            <input type="text" id="walletInput" placeholder="Enter MetaMask wallet address">
            <button onclick="connectWallet()" class="primary">Connect Wallet</button>
        </div>
    </div>

    <!-- Command Input -->
    <div class="input-group">
        <input type="text" id="commandInput" placeholder="Enter command: dance, spin 360, grab [x,y,z]">
        <button onclick="sendCommand()" class="primary" style="width:100%; margin-top:12px;">Execute Command</button>
    </div>

    <!-- Alert -->
    <div id="alert" class="alert"></div>

    <!-- Payment Section -->
    <div id="paymentSection" class="payment-section">
        <h3>Payment Required</h3>
        <p>Amount: <strong id="paymentAmount">100.00 ETH</strong></p>
        <button onclick="payWithETH()" class="primary">Pay with ETH</button>
    </div>

    <!-- Command History -->
    <div class="command-history">
        <h3>Recent Commands</h3>
        <div id="commandHistory"></div>
    </div>

    <!-- Joint Visualization -->
    <div id="robotVisualization" class="joint-visualization"></div>
    
    <!-- Footer -->
    <div class="footer">
        <a href="#">Tsion Dynamics</a> | 
        <a href="#">Documentation</a> | 
        <a href="#">GitHub</a>
    </div>

</div>

<script>
    // JavaScript implementation
    let currentWallet = null;
    let commands = [];

    function connectWallet() {
        const input = document.getElementById('walletInput').value;
        if (input && input.startsWith('0x') && input.length === 42) {
            currentWallet = input;
            document.getElementById('walletInfo').style.display = 'block';
            document.getElementById('connectWallet').style.display = 'none';
            document.getElementById('walletAddress').innerText = input.substring(0, 10) + '...' + input.substring(36);
            document.getElementById('walletBalance').innerText = '2.45 ETH';
            showAlert('Wallet connected successfully', 'success');
        } else {
            showAlert('Invalid wallet address. Must start with 0x and be 42 characters', 'error');
        }
    }

    function disconnectWallet() {
        currentWallet = null;
        document.getElementById('walletInfo').style.display = 'none';
        document.getElementById('connectWallet').style.display = 'block';
        document.getElementById('walletInput').value = '';
        showAlert('Wallet disconnected', 'success');
    }

    function sendCommand() {
        const command = document.getElementById('commandInput').value;
        if (!command) {
            showAlert('Please enter a command', 'error');
            return;
        }
        if (!currentWallet) {
            showAlert('Please connect wallet first', 'error');
            return;
        }
        
        const cost = calculateCost(command);
        
        if (cost > 0) {
            document.getElementById('paymentAmount').innerText = cost.toFixed(2) + ' ETH';
            document.getElementById('paymentSection').style.display = 'block';
            showAlert(`Command requires ${cost.toFixed(2)} ETH. Please complete payment.`, 'error');
        } else {
            executeCommand(command);
        }
    }

    function calculateCost(command) {
        const costs = {
            'dance': 50,
            'spin': 30,
            'grab': 100,
            'wave': 20,
            'reset': 0
        };
        for (let [key, value] of Object.entries(costs)) {
            if (command.toLowerCase().includes(key)) return value;
        }
        return 10;
    }

    function payWithETH() {
        showAlert('Processing payment...', 'success');
        setTimeout(() => {
            document.getElementById('paymentSection').style.display = 'none';
            executeCommand(document.getElementById('commandInput').value);
        }, 1500);
    }

    function executeCommand(command) {
        addToHistory(command, 'done');
        updateRobotVisualization(command);
        showAlert(`Command "${command}" executed successfully`, 'success');
        document.getElementById('commandInput').value = '';
    }

    function addToHistory(command, status) {
        commands.unshift({ command, status, time: new Date().toLocaleTimeString() });
        if (commands.length > 5) commands.pop();
        
        const historyDiv = document.getElementById('commandHistory');
        historyDiv.innerHTML = commands.map(cmd => `
            <div class="command-item">
                <span><strong>${cmd.command}</strong><br><small>${cmd.time}</small></span>
                <span class="status ${cmd.status}">${cmd.status.toUpperCase()}</span>
            </div>
        `).join('');
    }

    function updateRobotVisualization(command) {
        const joints = [
            { name: 'Base', value: 45 + Math.random() * 40 },
            { name: 'Shoulder', value: 30 + Math.random() * 50 },
            { name: 'Elbow', value: 60 + Math.random() * 30 },
            { name: 'Wrist 1', value: 20 + Math.random() * 60 },
            { name: 'Wrist 2', value: 50 + Math.random() * 40 },
            { name: 'Wrist 3', value: 70 + Math.random() * 25 }
        ];
        
        const vizDiv = document.getElementById('robotVisualization');
        vizDiv.innerHTML = '<h3>Joint Positions</h3>' + joints.map(joint => `
            <div class="joint">
                <div class="joint-label">${joint.name}</div>
                <div class="joint-bar">
                    <div class="joint-fill" style="width: ${joint.value}%;">${Math.round(joint.value)}%</div>
                </div>
            </div>
        `).join('');
    }

    function showAlert(message, type) {
        const alertDiv = document.getElementById('alert');
        alertDiv.className = `alert ${type}`;
        alertDiv.innerHTML = message;
        alertDiv.style.display = 'block';
        setTimeout(() => alertDiv.style.display = 'none', 3000);
    }
</script>
</body>
</html>
