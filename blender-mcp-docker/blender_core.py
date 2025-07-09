from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolDefinition:
    """tool definition with schema support"""
    name: str
    description: str
    handler: Callable[[dict], str]
    input_schema: Dict[str, Any]


TOOL_REGISTRY: Dict[str, ToolDefinition] = {}

def register_tool(name: str, description: str = "", input_schema: Optional[Dict[str, Any]] = None):
    """tool registration with schema support"""
    def decorator(func):
        desc = description or func.__doc__ or f"Tool: {name}"
        
        schema = input_schema or {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        TOOL_REGISTRY[name] = ToolDefinition(
            name=name,
            description=desc,
            handler=func,
            input_schema=schema
        )
        return func
    return decorator


PROMPT_REGISTRY: Dict[str, Callable[[], str]] = {}

def register_prompt(name: str):
    def decorator(func):
        PROMPT_REGISTRY[name] = func
        return func
    return decorator
