from mcp.server.fastmcp import FastMCP, Context, Image
import socket
import json
import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional
import os
from pathlib import Path
import base64
from urllib.parse import urlparse
from aiohttp import web
import aiohttp_cors
from aiohttp_sse import sse_response
import uuid
import weakref
import queue
import time
from blender_core import TOOL_REGISTRY, PROMPT_REGISTRY
from tool_set import * 


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlenderMCPServer")


@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None  
    
    def connect(self) -> bool:
        """Connect to the Blender addon socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Blender: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Blender addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Blender: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(15.0)  # Match the addon's timeout
        
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        # If we get here, it parsed successfully
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Blender and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(15.0)  # Match the addon's timeout
            
            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Blender error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Blender"))
            
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Blender")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Blender response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Blender lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Blender: {str(e)}")
            # Try to log what was received
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Blender: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Blender: {str(e)}")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            self.sock = None
            raise Exception(f"Communication error with Blender: {str(e)}")

# Global connection and notification management
_blender_connection = None
_polyhaven_enabled = False
_notification_clients = weakref.WeakSet()
_notification_queue = queue.Queue()

def get_blender_connection():
    """Get or create a persistent Blender connection"""
    global _blender_connection, _polyhaven_enabled
    
    # If we have an existing connection, check if it's still valid
    if _blender_connection is not None:
        try:
            # First check if PolyHaven is enabled by sending a ping command
            result = _blender_connection.send_command("get_polyhaven_status")
            # Store the PolyHaven status globally
            _polyhaven_enabled = result.get("enabled", False)
            return _blender_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _blender_connection.disconnect()
            except:
                pass
            _blender_connection = None
    
    # Create a new connection if needed
    if _blender_connection is None:
        _blender_connection = BlenderConnection(host="localhost", port=9876)
        if not _blender_connection.connect():
            logger.error("Failed to connect to Blender")
            _blender_connection = None
            raise Exception("Could not connect to Blender. Make sure the Blender addon is running.")
        logger.info("Created new persistent connection to Blender")
    
    return _blender_connection


class MCPHTTPServer:
    """HTTP-based MCP Server with SSE support"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.mcp = FastMCP(
            "BlenderMCP",
            description="Blender integration through the Model Context Protocol"
        )
        self.setup_routes()
    
    def setup_routes(self):
        """Setup HTTP routes for MCP endpoint"""
        # Enable CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        # MCP endpoint - handle both GET and POST
        resource = cors.add(self.app.router.add_resource('/mcp'))
        cors.add(resource.add_route('POST', self.handle_mcp_post))
        cors.add(resource.add_route('GET', self.handle_mcp_get))
        
        # Health check endpoint
        cors.add(self.app.router.add_get('/health', self.handle_health))
        
    
    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy"})
        
    async def handle_mcp_post(self, request):
        """Handle MCP POST requests"""
        try:
            # Parse the JSON-RPC request
            body = await request.json()
            logger.info(f"Received MCP request: {body.get('method', 'unknown')}")
            
            # Process the request through FastMCP
            response = await self.process_mcp_request(body)
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Error handling MCP POST: {str(e)}")
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": body.get('id') if 'body' in locals() else None
            }, status=500)
    
    async def handle_mcp_get(self, request):
        """Handle MCP GET requests with SSE for streaming"""
        try:
            # Check if client wants SSE
            accept_header = request.headers.get('Accept', '')
            if 'text/event-stream' in accept_header:
                return await self.handle_sse_stream(request)
            else:
                # Regular GET request - return server capabilities
                capabilities = {
                    "jsonrpc": "2.0",
                    "result": {
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "prompts": {},
                            "logging": {},
                            "experimental": {
                                "sse": True
                            }
                        },
                        "serverInfo": {
                            "name": "BlenderMCP",
                            "version": "1.0.0"
                        }
                    }
                }
                return web.json_response(capabilities)
                
        except Exception as e:
            logger.error(f"Error handling MCP GET: {str(e)}")
            return web.json_response({
                "error": f"Internal error: {str(e)}"
            }, status=500)
    
    async def handle_sse_stream(self, request):
        """Handle Server-Sent Events streaming"""
        async with sse_response(request) as resp:
            client_id = str(uuid.uuid4())
            logger.info(f"SSE client connected: {client_id}")
            
            # Add client to notification set
            _notification_clients.add(resp)
            
            try:
                # Send initial connection message
                await resp.send(json.dumps({
                    "type": "connection",
                    "client_id": client_id,
                    "message": "Connected to BlenderMCP SSE stream"
                }))
                
                # Keep connection alive and send notifications
                while True:
                    try:
                        # Check for notifications
                        try:
                            notification = _notification_queue.get_nowait()
                            await resp.send(json.dumps(notification))
                        except queue.Empty:
                            pass
                        
                        # Send heartbeat every 30 seconds
                        await resp.send(json.dumps({
                            "type": "heartbeat",
                            "timestamp": time.time()
                        }))
                        
                        await asyncio.sleep(30)
                        
                    except Exception as e:
                        logger.error(f"Error in SSE stream: {str(e)}")
                        break
                        
            except Exception as e:
                logger.error(f"SSE stream error: {str(e)}")
            finally:
                logger.info(f"SSE client disconnected: {client_id}")
                _notification_clients.discard(resp)
                
        return resp
    
    async def process_mcp_request(self, request_data):
        """Process MCP JSON-RPC request"""
        method = request_data.get('method')
        params = request_data.get('params', {})
        request_id = request_data.get('id')
        
        try:
            if method == 'initialize':
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "prompts": {},
                            "logging": {}
                        },
                        "serverInfo": {
                            "name": "BlenderMCP",
                            "version": "1.0.0"
                        }
                    },
                    "id": request_id
                }
                
            elif method == 'tools/call':
                tool = params.get("name")
                arguments = params.get("arguments", {})
                result = await self.call_tool(tool, arguments)
                print(result)
                return {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": result}]}, "id": request_id}
            
            elif method == 'tools/list':
                # tools/list with proper schema support
                tools = []
                for name, tool_def in TOOL_REGISTRY.items():
                    tools.append({
                        "name": tool_def.name,
                        "description": tool_def.description,
                        "inputSchema": tool_def.input_schema
                    })
                return {
                    "jsonrpc": "2.0",
                    "result": {"tools": tools},
                    "id": request_id
                }
            
            elif method == 'prompts/call':
                prompt = params.get("name")
                if prompt not in PROMPT_REGISTRY:
                    raise ValueError(f"Unknown prompt: {prompt}")
                result = PROMPT_REGISTRY[prompt]()
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": result}]},
                    "id": request_id
                }
            elif method == 'prompts/list':
                prompts = [{"name": name, "description": func.__doc__ or f"Prompt: {name}"} 
                        for name, func in PROMPT_REGISTRY.items()]
                return {
                    "jsonrpc": "2.0",
                    "result": {"prompts": prompts},
                    "id": request_id
                }
            return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method: {method}"}, "id": request_id}
        except Exception as e:
            return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": request_id}
        
    async def call_tool(self, tool_name: str, args: dict) -> str:
        try:
            if tool_name not in TOOL_REGISTRY:
                raise ValueError(f"Unknown tool: {tool_name}")
            tool_def = TOOL_REGISTRY[tool_name]
            return tool_def.handler(args)
        except Exception as e:
            return f"Error in tool '{tool_name}': {str(e)}"
        
    async def broadcast_notification(self, notification):
        """Broadcast notification to all SSE clients"""
        _notification_queue.put(notification)
        
        # Also send directly to active clients
        for client in list(_notification_clients):
            try:
                await client.send(json.dumps(notification))
            except Exception as e:
                logger.warning(f"Failed to send notification to client: {str(e)}")
                _notification_clients.discard(client)


def main():
    """Run the HTTP MCP server"""
    async def _async_main():
        server = MCPHTTPServer(host='0.0.0.0', port=8080)
        
        # Try to connect to Blender on startup
        try:
            blender = get_blender_connection()
            logger.info("Successfully connected to Blender on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Blender on startup: {str(e)}")
            logger.warning("Make sure the Blender addon is running before using Blender tools")
        

        logger.info("Starting BlenderMCP HTTP server on http://0.0.0.0:8080/mcp")
        
        runner = web.AppRunner(server.app)
        await runner.setup()
        site = web.TCPSite(runner, server.host, server.port)
        await site.start()
        
        logger.info(f"HTTP MCP server started successfully on http://{server.host}:{server.port}/mcp")
        logger.info("Available endpoints:")
        logger.info("  POST /mcp - MCP JSON-RPC requests")
        logger.info("  GET /mcp - Server capabilities (or SSE with Accept: text/event-stream)")
        logger.info("  GET /health - Health check")
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down server")
        finally:
            # Clean up Blender connection
            global _blender_connection
            if _blender_connection:
                _blender_connection.disconnect()
    
    asyncio.run(_async_main())

def server_main():
    """Entry point for external callers"""
    main()

if __name__ == "__main__":
    main()