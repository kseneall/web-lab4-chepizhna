import asyncio
import websockets
import json
import random

SYMBOLS = ["BTC", "ETH", "DOGE", "XRP"]

async def mock_feed(websocket):
    while True:
        data = {
            "symbol": random.choice(SYMBOLS),
            "price": round(random.uniform(0.1, 50000), 2)
        }
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)

async def main():
    async with websockets.serve(mock_feed, "localhost", 8777):
        print("Mock external WS server running on ws://localhost:8766")
        await asyncio.Future()

asyncio.run(main())
