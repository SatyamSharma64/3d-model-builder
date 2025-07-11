import json
import uuid
from fastapi import WebSocket
from app.active_clients import register_user, unregister_user
from app.monitor_resources import resource_monitor
from app.job_worker import job_queue

async def websocket_handler(websocket: WebSocket, user_id: str):
    await websocket.accept()

    await register_user(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                prompt = data.get("prompt")
                project_id = data.get("project_id", "default")
                
                if not prompt:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Missing prompt"
                    })
                    continue
                
                # Check if we can accept the job
                # resources = resource_monitor.check_resources()
                # if not resources["can_accept_job"]:
                #     await ws.send_str(json.dumps({
                #         "type": "error", 
                #         "message": "Server overloaded, try again later"
                #     }))
                #     continue
                
                # Queue the job instead of processing directly
                job_id = str(uuid.uuid4())
                await job_queue.add_job(job_id, prompt, user_id, project_id)
                
                # Cleanup old data
                await resource_monitor.cleanup_if_needed()
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                    
    finally:
        await unregister_user(user_id)
        print(f"🔌 Disconnected: {user_id}")

    # return ws
