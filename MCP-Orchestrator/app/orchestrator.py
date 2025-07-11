import httpx
import asyncio
import os
import json
import time
import openai
from app.blender_client import MCPHTTPClient
from dotenv import load_dotenv

from app.session_store import get_messages, append_message
from dotenv import load_dotenv
from app.ws_emitter import notify_user
load_dotenv()

class MCPConnectionManager:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = None
        self.connected = False
        self.lock = asyncio.Lock()
        self.last_used = 0
        self.connection_timeout = 300  # 5 minutes
    
    async def get_client(self):
        async with self.lock:
            now = time.time()
            
            # Reconnect if stale or not connected
            if (not self.connected or 
                now - self.last_used > self.connection_timeout):
                
                if self.client:
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                
                self.client = MCPHTTPClient(self.base_url)
                await self.client.connect()
                self.connected = True
            
            self.last_used = now
            return self.client

# Global connection manager
mcp_manager = MCPConnectionManager(os.environ.get("BLENDER_SERVER_URL"))


async def run_agent_loop_direct_groq(prompt: str, user_id: str, project_id: str, job_id: str):
    try:
        client = await mcp_manager.get_client()
    except:
        return "Unable to connect with Blender", None
    tools_raw = await client.list_tools()
    
    # Get strategy message
    strategy_prompt = await client.call_prompt("asset_creation_strategy", {})

    # Start message history
    messages = get_messages(user_id, project_id)
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": strategy_prompt})
    
    messages.append({"role": "user", "content": prompt})
    # append_message(user_id, project_id, {"role": "user", "content": prompt})

    # Register tools in OpenAI-compatible format
    openai_tools = []
    tool_lookup = {}

    for tool in tools_raw:
        name = tool["name"]
        description = tool.get("description", "")
        schema = tool.get("inputSchema", {"type": "object", "properties": {}})
        openai_tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": schema,
            }
        })
        tool_lookup[name] = schema

    # Prepare client
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    while True:
        payload = {
            "model": "llama3-70b-8192",
            "messages": messages,
            "tools": openai_tools,
            "tool_choice": "auto"
        }

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            data = response.json()

        msg = data["choices"][0]["message"]
        print("messages:", messages)
    
        if "tool_calls" in msg:
            tool_call = msg["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])

            result = await client.call_tool(tool_name, args)

            # Add tool_call + result to messages
            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": result
            })

            await notify_user(user_id, {
                "type": "agent_tool_call",
                "job_id": job_id,
                "tool": tool_name,
                "input": args,
                "output": result,
                "project_id": project_id
            })

        elif msg.get("content"):
            final_output = msg["content"]
            messages.append({"role": "assistant", "content": final_output})
            append_message(user_id, project_id, {"role": "assistant", "content": final_output})

            # Auto-export model
            base64data = await client.call_tool("export_model", {"export_format": "GLB"})

            # await notify_user(user_id, {
            #     "type": "job_completed",
            #     "job_id": job_id,
            #     "project_id": project_id,
            #     "result": final_output,
            #     "base64data": base64data
            # })

            await client.disconnect()
            return final_output, base64data

        else:
            # Safety fallback
            await client.disconnect()
            return "No response from model.", None

        time.sleep(60)
