from typing import List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

def to_langchain_messages(messages: List[dict]) -> List[BaseMessage]:
    converted = []
    for msg in messages:
        if msg["role"] == "system":
            converted.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            converted.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            converted.append(AIMessage(content=msg["content"]))
        else:
            raise ValueError(f"Unsupported message role: {msg['role']}")
    return converted
