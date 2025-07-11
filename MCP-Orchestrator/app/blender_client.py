import asyncio
import logging
import json
import os
from typing import Optional, Dict, Any, List
import aiohttp
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPHTTPClient:
    """MCP HTTP Client wrapper with SSE support."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.mcp_endpoint = f"{self.base_url}/mcp"
        self.session: Optional[aiohttp.ClientSession] = None
        self.client_id = str(uuid.uuid4())
        self.sse_task: Optional[asyncio.Task] = None
        
    async def connect(self):
        """Initialize the HTTP client session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100)
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': f'MCP-HTTP-Client/{self.client_id}'
                }
            )
        
        logger.info(f"HTTP client initialized for {self.base_url}")
        
        # Initialize connection with the server
        await self.initialize_connection()
        
        # List available tools
        tools = await self.list_tools()
        logger.info(f"Connected to server with tools: {[tool['name'] for tool in tools]}")
        
    async def disconnect(self):
        """Close the HTTP client session"""
        if self.sse_task and not self.sse_task.done():
            self.sse_task.cancel()
            try:
                await self.sse_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("HTTP client disconnected")
    
    async def initialize_connection(self):
        """Initialize the MCP connection"""
        request_data = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "MCP-HTTP-Client",
                    "version": "1.0.0"
                }
            },
            "id": str(uuid.uuid4())
        }
        
        response = await self.make_request(request_data)
        
        if 'error' in response:
            raise Exception(f"Initialization failed: {response['error']}")
        
        logger.info("MCP connection initialized successfully")
        return response['result']
    
    async def make_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        if not self.session:
            raise Exception("Client not connected. Call connect() first.")
        
        try:
            async with self.session.post(self.mcp_endpoint, json=request_data) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                result = await response.json()
                return result
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server"""
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        response = await self.make_request(request_data)
        
        if 'error' in response:
            raise Exception(f"Failed to list tools: {response['error']}")
        
        return response['result']['tools']
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from the server"""
        request_data = {
            "jsonrpc": "2.0",
            "method": "resources/list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        response = await self.make_request(request_data)
        
        if 'error' in response:
            logger.warning(f"Failed to list resources: {response['error']}")
            return []
        
        return response['result'].get('resources', [])
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource from the server"""
        request_data = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {
                "uri": uri
            },
            "id": str(uuid.uuid4())
        }
        
        response = await self.make_request(request_data)
        
        if 'error' in response:
            raise Exception(f"Failed to read resource: {response['error']}")
        
        # Extract text content from the response
        contents = response['result'].get('contents', [])
        if contents and contents[0].get('type') == 'text':
            return contents[0]['text']
        else:
            return json.dumps(response['result'], indent=2)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool on the server"""
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": str(uuid.uuid4())
        }
        
        response = await self.make_request(request_data)
        
        if 'error' in response:
            raise Exception(f"Tool call failed: {response['error']}")
        
        # Extract text content from the response
        content = response['result'].get('content', [])
        if content and content[0].get('type') == 'text':
            return content[0]['text']
        else:
            return json.dumps(response['result'], indent=2)
    
    async def call_prompt(self, prompt_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool on the server"""
        request_data = {
            "jsonrpc": "2.0",
            "method": "prompts/call",
            "params": {
                "name": prompt_name,
                "arguments": arguments or {}
            },
            "id": str(uuid.uuid4())
        }
        
        response = await self.make_request(request_data)
        
        if 'error' in response:
            raise Exception(f"Prompt call failed: {response['error']}")
        
        # Extract text content from the response
        content = response['result'].get('content', [])
        if content and content[0].get('type') == 'text':
            return content[0]['text']
        else:
            return json.dumps(response['result'], indent=2)
    

    async def start_sse_listener(self, on_message_callback=None):
        """Start listening to Server-Sent Events"""
        if self.sse_task and not self.sse_task.done():
            logger.warning("SSE listener already running")
            return
        
        self.sse_task = asyncio.create_task(
            self._sse_listener(on_message_callback)
        )
        logger.info("Started SSE listener")
    
    async def _sse_listener(self, on_message_callback=None):
        """Internal SSE listener implementation"""
        if not self.session:
            raise Exception("Client not connected")
        
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        try:
            async with self.session.get(self.mcp_endpoint, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"SSE connection failed: HTTP {response.status}")
                
                logger.info("SSE connection established")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            message = json.loads(data)
                            logger.info(f"SSE message: {message.get('type', 'unknown')}")
                            
                            if on_message_callback:
                                await on_message_callback(message)
                            else:
                                await self._default_message_handler(message)
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in SSE message: {data}")
                            
        except asyncio.CancelledError:
            logger.info("SSE listener cancelled")
            raise
        except Exception as e:
            logger.error(f"SSE listener error: {str(e)}")
            raise
    
    async def _default_message_handler(self, message: Dict[str, Any]):
        """Default handler for SSE messages"""
        msg_type = message.get('type', 'unknown')
        
        if msg_type == 'connection':
            logger.info(f"SSE connection established: {message.get('message')}")
        elif msg_type == 'heartbeat':
            logger.debug(f"SSE heartbeat at {message.get('timestamp')}")
        elif msg_type == 'notification':
            logger.info(f"Server notification: {message.get('message')}")
        else:
            logger.info(f"Unknown SSE message type: {msg_type}")
    
    async def get_server_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities via GET request"""
        if not self.session:
            raise Exception("Client not connected")
        
        async with self.session.get(self.mcp_endpoint) as response:
            if response.status != 200:
                raise Exception(f"Failed to get capabilities: HTTP {response.status}")
            
            result = await response.json()
            return result.get('result', {})
    
    async def health_check(self) -> bool:
        """Check if the server is healthy"""
        if not self.session:
            return False
        
        try:
            health_url = f"{self.base_url}/health"
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('status') == 'healthy'
        except Exception:
            pass
        
        return False
    
    async def process_query(self) -> str:
        """Process a sample query using available tools"""
        final_text = []
        
        try:
            # List all available tools
            tools = await self.list_tools()
            final_text.append(f"Available tools: {[tool['name'] for tool in tools]}")
            
            # Call get_scene_info tool if available
            tool_names = [tool['name'] for tool in tools]
            if "get_scene_info" in tool_names:
                result = await self.call_tool("get_scene_info")
                final_text.append(f"[Scene Info Result]:\n{result}")
            else:
                final_text.append("Tool 'get_scene_info' not available")

            base64data = await self.call_tool("export_model", {"export_fromat": "GLB"})
            print(base64data)
            
        except Exception as e:
            final_text.append(f"Error during query processing: {str(e)}")
        
        return "\n\n".join(final_text)


async def main():
    """Main function to demonstrate the MCP HTTP client"""
    
    server_url = os.environ.get("BLENDER_SERVER_URL")
    
    client = MCPHTTPClient(server_url)
    
    try:
        # Connect to the server
        await client.connect()
        
        # Check server health
        is_healthy = await client.health_check()
        print(f"Server health: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
        
        # Optionally start SSE listener
        # await client.start_sse_listener()
        
        # sample query
        response = await client.process_query()
        print("\n" + "="*50)
        print("QUERY RESPONSE:")
        print("="*50)
        print(response)
        
        # Keep SSE listener running for a bit if started
        # await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())