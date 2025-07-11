from app.active_clients import get_user_ws
import json

async def notify_user(user_id: str, data: dict):
    ws = await get_user_ws(user_id)
    if ws:
        try:
            await ws.send_json(data)
        except:
            print(f"Failed to send to {user_id}, cleaning up.")
