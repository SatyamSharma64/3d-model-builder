from typing import Any, Dict, List
from langchain_core.callbacks.base import AsyncCallbackHandler
from ..ws_emitter import notify_user 

class WebSocketAgentCallbackHandler(AsyncCallbackHandler):
    def __init__(self, user_id: str, project_id: str, job_id: str):
        self.user_id = user_id
        self.project_id = project_id
        self.job_id = job_id

    async def _send(self, message: str):
        await notify_user(self.user_id, {
            "type": "agent_debug",
            "job_id": self.job_id,
            "project_id": self.project_id,
            "message": message
        })

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        print(f"DEBUG: LLM started with prompts: {prompts}")
        await self._send(f"Thinking...\n\n{prompts[0]}")

    async def on_llm_end(self, response, **kwargs) -> None:
        print(f"DEBUG: LLM ended with response: {response}")
        await self._send("LLM responded.")

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        print(f"DEBUG: Tool started - {serialized.get('name', 'unknown')} with input: {input_str}")
        await self._send(f"Using tool `{serialized.get('name', 'unknown')}` with input:{input_str}")

    async def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"DEBUG: Tool ended with output: {output}")
        await self._send(f"Tool completed with result:\n{output}")

    async def on_tool_error(self, error: Exception, **kwargs) -> None:
        print(f"DEBUG: Tool error: {error}")
        await self._send(f"DEBUG: Tool error: {error}")
        
    async def on_agent_action(self, action, **kwargs) -> None:
        print(f"DEBUG: Agent action: {action.tool} with input: {action.tool_input}")
        await self._send(f"Agent decided to use tool:\n```json\n{action.tool}\n```\nArgs:\n```json\n{action.tool_input}\n```")

    async def on_agent_finish(self, finish, **kwargs) -> None:
        print(f"DEBUG: Agent finished with: {finish.return_values}")
        await self._send(f"Agent finished with result:\n{finish.return_values['output']}")

    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        print(f"DEBUG: Chain started with inputs: {inputs}")
        await self._send(f"DEBUG: Chain started with inputs: {inputs}")
        
    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print(f"DEBUG: Chain ended with outputs: {outputs}")
        await self._send(f"DEBUG: Chain ended with outputs: {outputs}")
        
    async def on_chain_error(self, error: Exception, **kwargs) -> None:
        print(f"DEBUG: Chain error: {error}")
        await self._send(f"DEBUG: Chain error: {error}")
        
    async def on_text(self, text: str, **kwargs) -> None:
        print(f"DEBUG: Text callback: {text}")
        await self._send(f"DEBUG: Text callback: {text}")