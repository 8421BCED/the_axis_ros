<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>UR5 • Robot Commander | Tsion Dynamics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

    <style>
        * { box-sizing: border-box; margin:0; padding:0; font-family:'Inter', sans-serif; }
        body { background:#f4f7fc; min-height:100vh; display:flex; justify-content:center; padding:24px; }
        .container { width:100%; max-width:900px; background:#fff; border-radius:24px; box-shadow:0 20px 40px -12px rgba(0,20,40,0.25); padding:32px; border:1px solid #eaedf2; }

        /* Header */
        .header { text-align:center; margin-bottom:28px; }
        .header img { width:120px; display:block; margin:0 auto; }
        .header h1 { font-size:2rem; margin-top:12px; color:#1a2639; letter-spacing:-0.02em; }
        .header h1 span { font-size:0.8rem; background:#1a2639; color:white; padding:4px 12px; border-radius:40px; font-weight:400; }

        /* Sponsor */
        .sponsor { display:flex; align-items:center; justify-content:center; gap:16px; margin-bottom:24px; }
        .sponsor img { height:48px; }

        /* Video card */
        .video-card { background:#f9fbfd; border-radius:18px; padding:16px; border:1px solid #e2e9f2; margin-bottom:24px; text-align:center; }
        .video-card video { width:100%; border-radius:16px; max-height:350px; }

        /* Wallet Section */
        .wallet-section { background:#f9fbfd; border-radius:18px; padding:20px 24px; margin:24px 0 28px 0; border:1px solid #e2e9f2; }
        .wallet-section h3 { margin-bottom:16px; color:#1e2b3c; }
        #walletInfo p { display:flex; align-items:center; gap:12px; font-size:0.95rem; color:#2d3f56; flex-wrap:wrap; }
        #walletAddress, #walletBalance { border-radius:40px; padding:8px 16px; font-family:'Fira Code', monospace; font-size:0.9rem; }
        #walletAddress { background:white; border:1px solid #d0ddee; color:#0b1c2e; }
        #walletBalance { background:#e8f0fe; border:1px solid #b9d1f0; font-weight:600; color:#1e3e6e; }
        #connectWallet input { width:100%; padding:14px 18px; border-radius:14px; border:1px solid #cfddee; margin-bottom:12px; }
        #connectWallet input:focus { outline:none; border-color:#3a7bd5; box-shadow:0 0 0 3px rgba(58,123,213,0.08); }

        /* Buttons */
        button { border:none; padding:10px 22px; font-size:0.95rem; font-weight:450; border-radius:40px; cursor:pointer; transition:0.15s; margin:0 6px 6px 0; box-shadow:0 2px 6px rgba(0,20,40,0.08); }
        button.primary { background:#1e2f4a; color:white; }
        button.primary:hover { background:#253c5c; box-shadow:0 8px 14px -8px rgba(20,60,120,0.3); transform:translateY(-1px); }
        button.secondary { background:#fff; color:#1e2f4a; border:1px solid #c8d5e6; }
        button.secondary:hover { background:#f2f7ff; transform:translateY(-1px); }

        .input-group { margin:24px 0; }
        #commandInput { width:100%; padding:16px 20px; font-size:1rem; border:1px solid #dae2ed; border-radius:18px; margin-bottom:16px; }
        #commandInput:focus { border-color:#3a7bd5; outline:none; box-shadow:0 0 0 4px rgba(58,123,213,0.08); }

        /* Alerts */
        .alert { padding:16px 22px; border-radius:60px; margin:20px 0; display:none; font-weight:450; font-size:0.95rem; }
        .alert.success { background:#f1f9f0; color:#1d5a3e; border:1px solid #a8d5b5; }
        .alert.error { background:#fee9e7; color:#a12b2b; border:1px solid #fbb4b4; }

        /* Payment */
        .payment-section { background:#f2f7ff; border-radius:20px; padding:20px 26px; margin:28px 0 20px; display:none; border:1px solid #bfd6f0; }
        .payment-section h3 { margin-top:0; color:#1e3e6e; }
        .payment-section p { margin:12px 0; color:#1a2f48; }
        .payment-section strong { padding:4px 12px; border-radius:30px; border:1px solid #b9d1f0; background:#ffffffb0; font-weight:600; }

        /* Command History */
        .command-history { margin:32px 0 10px; background:#fafcff; border-radius:20px; padding:12px; }
        .command-item { background:#fff; padding:14px 18px; margin:10px 0; border-radius:16px; border:1px solid #e6ecf5; display:flex; justify-content:space-between; flex-wrap:wrap; box-shadow:0 2px 6px #eef3f9; }
        .status { font-size:0.8rem; font-weight:500; padding:5px 12px; border-radius:40px; min-width:85px; text-align:center; }
        .status.done { background:#e2f3e4; color:#166b3b; border:1px solid #b2e0ba; }
        .status.error { background:#fde4e1; color:#bb2d2d; border:1px solid #fbc1bc; }
        .status.paid { background:#ece3ff; color:#583c9e; border:1px solid #cbb8ff; }

        /* Joint Visualization */
        .joint-visualization { margin:32px 0 8px; background:#f9fcff; border-radius:20px; padding:22px; border:1px solid #e2ecfb; }
        .joint { margin:14px 0; }
        .joint-label { font-size:0.8rem; font-weight:500; color:#3e5670; margin-bottom:5px; text-transform:uppercase; letter-spacing:0.3px; }
        .joint-bar { height:24px; background:#e2e9f2; border-radius:40px; overflow:hidden; box-shadow: inset 0 1px 4px #d0dcee; }
        .joint-fill { height:100%; color:white; text-align:center; font-size:0.75rem; font-weight:500; line-height:24px; transition:width 0.5s ease; text-shadow:0 1px 2px rgba(0,0,0,0.2); background:#3a6ea5; }

    </style>
</head>
<body>
    <div class="container">

        <!-- Header + Logo -->
        <div class="header">
            <img src="/static/tsion.jpeg" alt="Tsion Dynamics Logo">
            <h1>UR5 <span>Controller</span></h1>
        </div>

        <!-- Sponsor Logos -->
        <div class="sponsor">
            <img src="/static/hdeth.png" alt="Ethereum Foundation Logo">
            <span style="font-size:0.9rem; color:#2c3e50;">Supported by Ethereum Foundation: <a href="https://ethereum.foundation/" target="_blank">ethereum.foundation</a></span>
        </div>

        <!-- Robot Demo Video -->
        <div class="video-card">
            <video src="/static/159021-818026286.mp4" controls autoplay loop muted></video>
        </div>

        <!-- Wallet Section -->
        <div class="wallet-section">
            <h3>Wallet connection</h3>
            <div id="walletInfo" style="display:none;">
                <p>
                    Connected account: <strong id="walletAddress"></strong>
                    Balance: <span id="walletBalance">0 ETH</span>
                    <button onclick="disconnectWallet()">Disconnect</button>
                </p>
            </div>
            <div id="connectWallet">
                <input type="text" id="walletInput" placeholder="Paste MetaMask wallet address">
                <button onclick="connectWallet()" class="primary">Connect Wallet</button>
            </div>
        </div>

        <!-- Command Input -->
        <div class="input-group">
            <input type="text" id="commandInput" placeholder="Enter command, e.g. dance, spin 360">
            <button onclick="sendCommand()" class="primary" style="width:100%; margin-top:12px;">Execute Command</button>
        </div>

        <!-- Alert -->
        <div id="alert" class="alert"></div>

        <!-- Payment Section -->
        <div id="paymentSection" class="payment-section">
            <h3>Payment required</h3>
            <p>Amount: <strong id="paymentAmount">100.00 ETH</strong></p>
            <div class="flex-row">
                <button onclick="payWithETH()" class="primary">Pay ETH</button>
            </div>
        </div>

        <!-- Command History -->
        <div class="command-history">
            <h3>Recent commands</h3>
            <div id="commandHistory"></div>
        </div>

        <!-- Joint Visualization -->
        <div id="robotVisualization" class="joint-visualization"></div>

    </div>

    <script>
        // --- JS logic remains identical to your previous backend -- Wallet, Commands, Payment, LLM to ROS2 ---
        // Copy all previous JS code here (connectWallet, sendCommand, payWithETH, updateRobotVisualization...)
    </script>
</body>
</html>
