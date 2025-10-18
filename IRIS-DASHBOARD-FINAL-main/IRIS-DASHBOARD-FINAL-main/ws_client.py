import asyncio
import json
import websockets
import os

class DashboardWebSocketClient:
    """Connects to backend WebSocket server to receive live updates."""
    def __init__(self, uri=None):
        self.uri = uri or os.getenv("IRS_WS_URL", "ws://localhost:8765")
        self.on_message = None  # callback function

    async def listen(self):
        """Connect and listen for messages."""
        try:
            async with websockets.connect(self.uri) as ws:
                print(f"[WS] Connected to backend at {self.uri}")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if self.on_message:
                        self.on_message(data)
        except Exception as e:
            print(f"[WS] Connection error: {e}")
            await asyncio.sleep(2)
            await self.listen()  # retry on disconnect

    def start(self):
        """Creates a new event loop and runs the listener."""
        try:
            # asyncio.run() handles loop creation and cleanup automatically.
            asyncio.run(self.listen())
        except KeyboardInterrupt:
            print("[WS] WebSocket client stopped.")