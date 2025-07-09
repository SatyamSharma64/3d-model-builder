from typing import List, Dict, Any
from langchain.tools import StructuredTool
from pydantic import create_model
import asyncio
import threading
import concurrent.futures

def mcp_tools_factory(tools: List[Dict[str, Any]], client):
    """Auto-wrap MCP tools into LangChain StructuredTool objects."""
    langchain_tools = []

    for tool in tools:
        name = tool["name"]
        description = tool.get("description", "")
        input_schema = tool.get("inputSchema", {"type": "object", "properties": {}})

        properties = input_schema.get("properties", {})
        required_fields = input_schema.get("required", [])

        # Create a Pydantic model dynamically
        model_fields = {}
        for key, val in properties.items():
            # Handle different types properly
            if val.get("type") == "string":
                field_type = str
            elif val.get("type") == "integer":
                field_type = int
            elif val.get("type") == "number":
                field_type = float
            elif val.get("type") == "boolean":
                field_type = bool
            elif val.get("type") == "array":
                field_type = list
            elif val.get("type") == "object":
                field_type = dict
            else:
                field_type = str  # Default to string
            
            # Set default value based on whether field is required
            if key in required_fields:
                model_fields[key] = (field_type, ...)
            else:
                model_fields[key] = (field_type, None)

        # Handle empty schemas
        if not model_fields:
            model_fields["dummy"] = (str, None)

        ToolInputModel = create_model(f"{name.capitalize().replace('_', '')}Input", **model_fields)

        # Create closure to capture the tool name
        def make_tool_function(tool_name):
            def sync_func(**kwargs):
                try:
                    # Remove dummy field if it exists
                    if "dummy" in kwargs:
                        kwargs.pop("dummy")
                    
                    print(f"DEBUG: Calling tool {tool_name} with args: {kwargs}")
                    
                    # Use thread pool to run async function
                    def run_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            return loop.run_until_complete(client.call_tool(tool_name, kwargs))
                        finally:
                            loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_async)
                        result = future.result(timeout=30)  # 30 second timeout
                        print(f"DEBUG: Tool {tool_name} returned: {result}")
                        return result
                        
                except Exception as e:
                    error_msg = f"Error calling {tool_name}: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    return error_msg
            
            return sync_func

        sync_func = make_tool_function(name)

        tool_obj = StructuredTool.from_function(
            name=name,
            description=description,
            func=sync_func,
            args_schema=ToolInputModel,
        )
        langchain_tools.append(tool_obj)

    print(f"Created {len(langchain_tools)} LangChain tools: {[t.name for t in langchain_tools]}")
    return langchain_tools
