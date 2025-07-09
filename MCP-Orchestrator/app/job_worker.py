import asyncio
from collections import deque
import time
from app.orchestrator import run_agent_loop_direct_groq
from app.mcp_orchestrator import run_agent_on_prompt
from app.ws_emitter import notify_user

class SingleInstanceJobQueue:
    def __init__(self):
        self.queue = deque()
        self.current_job = None
        self.processing = False
        self.job_results = {}  
    
    async def add_job(self, job_id: str, prompt: str, user_id: str, project_id: str):
        job = {
            "id": job_id,
            "prompt": prompt,
            "user_id": user_id,
            "project_id": project_id,
            "created_at": time.time(),
            "status": "queued"
        }
        self.queue.append(job)
        
        # Notifying queue position
        position = len(self.queue)
        await notify_user(user_id, {
            "type": "job_queued",
            "job_id": job_id,
            "position": position,
            "estimated_wait": position * 30  # 30 seconds per job estimate
        })
        
        if not self.processing:
            asyncio.create_task(self.process_queue())
    
    async def process_queue(self):
        if self.processing:
            return
        
        self.processing = True
        
        while self.queue:
            job = self.queue.popleft()
            self.current_job = job
            
            try:
                # Notify job started
                await notify_user(job["user_id"], {
                    "type": "job_started",
                    "job_id": job["id"],
                    "project_id": job["project_id"]
                })
                
                # Process the job
                # result, base64data = await run_agent_on_prompt(
                #     job["prompt"], 
                #     job["user_id"], 
                #     job["project_id"],
                #     job["id"]
                # )

                result, base64data = await run_agent_loop_direct_groq(
                    job["prompt"], 
                    job["user_id"], 
                    job["project_id"],
                    job["id"]
                )
                
                # Store result and notify
                self.job_results[job["id"]] = result
                await notify_user(job["user_id"], {
                    "type": "job_completed",
                    "job_id": job["id"],
                    "project_id": job["project_id"],
                    "result": result,
                    "base64data": base64data
                })
                
            except Exception as e:
                await notify_user(job["user_id"], {
                    "type": "job_failed",
                    "job_id": job["id"],
                    "project_id": job["project_id"],
                    "error": str(e)
                })
            
            self.current_job = None
        
        self.processing = False

# Global queue instance
job_queue = SingleInstanceJobQueue()


# import asyncio
# import os
# import redis.asyncio as redis
# import json
# from mcp_orchestrator import run_agent_on_prompt
# from ws_emitter import notify_user

# async def listen_to_queue():
#     redis = redis.Redis(os.environ["REDIS_URL"])
#     print("MCP Orchestrator is listening for jobs...")

#     while True:
#         # Blocking pop from queue
#         job = await redis.blpop("blender-commands", timeout=0)
#         if job:
#             _, raw_data = job
#             job_data = json.loads(raw_data)

#             job_id = job_data["job_id"]
#             prompt = job_data["prompt"]
#             user_id = job_data["user_id"]
#             project_id = job_data["project_id"]

#             await notify_user(user_id, {
#                 "type": "job_started",
#                 "job_id": job_id,
#                 "prompt": prompt
#                 })
            

#             print(f"Processing Job {job_id} for {user_id}: {prompt}")

#             try:
#                 result = await run_agent_on_prompt(prompt, user_id, project_id)
#                 # await redis.set(f"job_result:{job_id}", json.dumps({"status": "done", "result": result}))
#                 await notify_user(user_id, {
#                     "type": "job_result",
#                     "job_id": job_id,
#                     "result": result["message"],
#                     "preview_url": result["preview_url"]
#                     })
#             except Exception as e:
#                 await redis.set(f"job_result:{job_id}", json.dumps({"status": "error", "error": str(e)}))
