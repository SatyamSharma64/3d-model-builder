from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.ws_server import websocket_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_handler(websocket, user_id)

# async def on_startup(app):
#     app["queue_worker"] = asyncio.create_task(listen_to_queue())

# async def on_cleanup(app):
#     app["queue_worker"].cancel()

# app.on_startup.append(on_startup)
# app.on_cleanup.append(on_cleanup)

# web.run_app(app, port=4003)
