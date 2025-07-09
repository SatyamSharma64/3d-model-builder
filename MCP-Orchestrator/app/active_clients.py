import asyncio

# Stores: user_id → WebSocket instance
connected_users = {}
connected_users_lock = asyncio.Lock()

async def register_user(user_id: str, ws):
    async with connected_users_lock:
        connected_users[user_id] = ws

async def unregister_user(user_id: str):
    async with connected_users_lock:
        connected_users.pop(user_id, None)

async def get_user_ws(user_id: str):
    async with connected_users_lock:
        return connected_users.get(user_id)
