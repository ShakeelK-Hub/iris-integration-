# ws_simulator.py — minimal backend simulator for the dashboard
import asyncio, json, random, time
import websockets

HOST = "localhost"
PORT = 8765

async def server():
    clients = set()

    async def handler(ws):
        clients.add(ws)
        print(f"[SIM] Dashboard connected ({len(clients)} clients)")
        try:
            async for _ in ws:  # we ignore incoming messages; push-only
                pass
        finally:
            clients.discard(ws)
            print(f"[SIM] Dashboard disconnected ({len(clients)} remaining)")

    async with websockets.serve(handler, HOST, PORT):
        print(f"[SIM] WebSocket simulator running at ws://{HOST}:{PORT}")
        start = time.time()
        session_id = 1
        while True:
            elapsed = time.time() - start
            status = "Alert" if int(elapsed) % 10 < 7 else "Drowsy"
            state = {
                "connected": True,
                "session_id": session_id,
                "duration": round(elapsed, 1),
                "status": status,
                "metrics": {
                    "blink_duration": round(random.uniform(200, 420), 1),
                    "avg_accel": round(random.uniform(0.02, 0.12), 3),
                    "nod_freq": round(random.uniform(0.0, 0.6), 2)
                }
            }
            # broadcast to all connected dashboards
            if clients:
                msg = json.dumps(state)
                await asyncio.gather(*(c.send(msg) for c in list(clients)))
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(server())
    except KeyboardInterrupt:
        print("\n[SIM] Stopped.")
