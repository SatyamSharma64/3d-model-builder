import asyncio
from aiohttp import web
from app.ws_server import websocket_handler


app = web.Application()

app.router.add_get("/ws", websocket_handler)

# async def on_startup(app):
#     app["queue_worker"] = asyncio.create_task(listen_to_queue())

# async def on_cleanup(app):
#     app["queue_worker"].cancel()

# app.on_startup.append(on_startup)
# app.on_cleanup.append(on_cleanup)

web.run_app(app, port=4003)
