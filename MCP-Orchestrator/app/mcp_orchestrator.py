import asyncio
import os
import json
import time
import openai
from app.blender_client import MCPHTTPClient
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

from app.agent.agent_message_wrapper import to_langchain_messages
from app.agent.agent_tools import mcp_tools_factory
from app.agent.callback_handler import WebSocketAgentCallbackHandler
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

groq_llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-70b-8192",  
    temperature=0.5
)

async def run_agent_on_prompt(prompt: str, user_id: str, project_id: str, job_id: str):
    # try:
        # Step 1: Get MCP tool list and client
        client = await mcp_manager.get_client()
        tools_raw = await client.list_tools()
        print("tools_raw",tools_raw)
        langchain_tools = mcp_tools_factory(tools_raw, client)
        
        # Step 2: Get strategy system message
        strategy_prompt = await client.call_tool("asset_creation_strategy", {})

        # Step 3: Prepare session
        messages = get_messages(user_id, project_id)
        if not any(m["role"] == "system" for m in messages):
            messages.insert(0, {"role": "system", "content": strategy_prompt})

        messages.append({"role": "user", "content": prompt})
        append_message(user_id, project_id, {"role": "user", "content": prompt})

        chat_history = to_langchain_messages(get_messages(user_id, project_id))

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", strategy_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad") 
        ])
        
        agent = create_openai_functions_agent(
            llm=groq_llm,
            tools=langchain_tools,
            prompt=prompt_template
        )
        callback_handler = WebSocketAgentCallbackHandler(user_id, project_id, job_id)

        executor = AgentExecutor(
            agent=agent,
            tools=langchain_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True
        )

        # Step 5: Run agent
        result = await executor.ainvoke(
            {"input": prompt, "chat_history": chat_history},
            callbacks=[callback_handler]
        )

        final_output = result.get("output", "")
        messages.append({"role": "assistant", "content": final_output})
        append_message(user_id, project_id, {"role": "assistant", "content": final_output})

        # Step 6: Auto-call export_model tool
        export_result = await client.call_tool("export_model", {"export_format": "GLB"})
        base64data = json.loads(export_result).get("data", "")

        await client.disconnect()
        return final_output, base64data

    # except Exception as e:
        # return f"failed with error: {e}", None
        # raise

