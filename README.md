# 🚀 IRIS Integration — Detection Service ↔ Dashboard

This document explains **step-by-step** how the **IRIS Detection Service (backend)** and the **IRIS Dashboard (frontend)** are connected, what was changed for integration, and how to run it on **any PC**.

---

## 🧠 Overview

| Component | Role | Connection Type |
|------------|------|-----------------|
| **IRIS Detection Service** | Backend that collects BLE data and broadcasts drowsiness metrics | 🖥️ WebSocket **Server** |
| **IRIS Dashboard** | Frontend that receives data and displays driver state | 📊 WebSocket **Client** |

**Protocol:** WebSocket  
**Default URL:** `ws://localhost:8765`  
**Data Flow:** Service ➜ Dashboard  

---

## ⚙️ Integration Summary

Integration required adding **one line of code** to enable the backend to broadcast data automatically.

**File Edited:**  
`IRIS-Detection-Service/service/src/controller.py`

```python
# After WebSocket server starts
asyncio.create_task(broadcast_state())
✅ This makes the service continuously send JSON data to the dashboard every second.

📁 Folder Structure
plaintext
Copy code
iris-integration/
│
├── IRIS-Detection-Service/
│   └── service/
│       └── src/
│           ├── controller.py
│           ├── network/ws_server.py
│           └── ...
│
├── IRIS-Dashboard/
│   ├── run_dashboard.py
│   ├── ws_client.py
│   └── ...
│
└── README.md
🪄 Step 1 — Run the Detection Service (Backend)
🧰 Commands for Windows PowerShell
powershell
Copy code
# Go to the service folder
cd ".\IRIS-Detection-Service\service"

# Create and activate a Python 3.11 virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade basic tools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
python -m pip install numpy pandas scipy hmmlearn joblib bleak websockets

# Create a baseline file so the service can start
python -c "import json; json.dump({'blink_baseline_ms':300,'nod_freq_baseline_hz':0.1,'accel_baseline_g':0.05}, open('drowsiness_baseline.json','w'))"

# Move up one folder and start the service
cd ..
python -m service.src.controller
✅ Expected Output:

csharp
Copy code
[INFO] Scanning for BLE device 'AntiSleepGlasses'...
[INFO] WebSocket server started at ws://127.0.0.1:8765
⚠️ BLE Error Example (Safe to Ignore):

vbnet
Copy code
[ERROR] BLE error: [WinError -2147020577] The device is not ready for use.
This only appears when the BLE device isn’t connected — it does not affect the integration.

🧭 Step 2 — Run the Dashboard (Frontend)
🪟 PowerShell Commands
powershell
Copy code
# Open a new PowerShell window
cd ".\IRIS-Dashboard"

# Create and activate virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install websockets PySimpleGUI

# Point the dashboard to the service
$env:IRIS_WS_URL = "ws://localhost:8765"

# Run the dashboard
python run_dashboard.py
💡 If PySimpleGUI gives errors, skip the GUI and move to Step 3 to verify integration without it.

🧩 Step 3 — Verify Integration (Without GUI)
This step confirms the dashboard can receive messages from the backend.

🖥️ PowerShell Command
powershell
Copy code
$env:IRIS_WS_URL = "ws://localhost:8765"
@'
import os, asyncio, json
import websockets
uri = os.getenv("IRIS_WS_URL", "ws://localhost:8765")
async def main():
    print(f"[CLIENT] Connecting to {uri} ...")
    async with websockets.connect(uri) as ws:
        print("[CLIENT] Connected. Printing 5 messages:")
        for _ in range(5):
            print(await ws.recv())
asyncio.run(main())
'@ | python -
✅ Expected Output:

csharp
Copy code
[CLIENT] Connecting to ws://localhost:8765 ...
[CLIENT] Connected. Printing 5 messages:
{"connected": true, "session_id": 1, "status": "Alert", "metrics": {...}}
...
🎯 This confirms successful communication between backend and frontend.

🌐 Step 4 — Running on Two Different PCs (LAN Setup)
🖥️ On the Service PC
powershell
Copy code
# Start the service
python -m service.src.controller

# Find local IP address
ipconfig
Example: 192.168.1.50

💡 Make sure TCP port 8765 is open on the firewall.

💻 On the Dashboard PC
powershell
Copy code
cd ".\IRIS-Dashboard"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install websockets
$env:IRIS_WS_URL = "ws://192.168.1.50:8765"
python run_dashboard.py
✅ The dashboard will now connect to the service running on the other machine.

⚙️ Troubleshooting
Issue Cause Fix
OSError 10048 Port 8765 is already in use Close the old instance or change port in ws_server.py
BLE not ready No device connected Safe to ignore
Missing baseline file No drowsiness_baseline.json found Run the one-liner in Step 1
ModuleNotFoundError: src Running from wrong directory Use python -m service.src.controller from parent folder
PySimpleGUI error GUI library version mismatch Skip GUI and verify via Step 3

✅ Integration Verification Checklist
 Backend starts and shows “WebSocket server started”.

 Dashboard or test client connects and prints JSON data.

 IRIS_WS_URL variable works for connection changes.

 drowsiness_baseline.json exists and service runs cleanly.

 Works across LAN if port 8765 is open.

Once all are checked, ✅ integration is complete.

📷 Suggested Proof for Report or Handover
Screenshot of Service Console — shows WebSocket started message.

Screenshot of Dashboard/Client Console — shows connected messages and data stream.

📦 Deliverables
README.md (this file)

Working folder structure:

Copy code
IRIS-Detection-Service/
IRIS-Dashboard/
Optional: .venv or requirements.txt

2 proof screenshots (Service + Dashboard)

🏁 Summary
Item Description
Connection Type WebSocket (ws://<host>:8765)
Service Role Sends continuous JSON data
Dashboard Role Receives and displays JSON updates
Change Made Added asyncio.create_task(broadcast_state())
Integration Status ✅ Verified and Complete

Maintainer: Shakeel Khan
Purpose: Demonstrate successful WebSocket integration between IRIS Detection Service and IRIS Dashboard
Status: ✔️ Finalized and Working
Last Verified: 2025-10-18