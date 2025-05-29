from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import asyncio
import websockets
import json

clients = set()
EXTERNAL_WS = "ws://localhost:8777"

def transform(data: dict) -> dict:
    return {
        "symbol": data.get("symbol"),
        "price": round(float(data.get("price", 0)), 2)
    }

async def broadcast(msg: str):
    for ws in list(clients):
        try:
            await ws.send_text(msg)
        except:
            clients.remove(ws)

async def relay_external_data():
    while True:
        try:
            async with websockets.connect(EXTERNAL_WS) as ext_ws:
                async for msg in ext_ws:
                    parsed = json.loads(msg)
                    transformed = json.dumps(transform(parsed))
                    await broadcast(transformed)
        except Exception as e:
            print(f"[!] External WS error: {e}")
            await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(relay_external_data())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        clients.remove(websocket)
