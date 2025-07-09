from collections import defaultdict
from typing import Dict, List

# Stores: (user_id, project_id) → [OpenAI messages]
session_messages: Dict[str, List[dict]] = defaultdict(list)

def session_key(user_id: str, project_id: str) -> str:
    return f"{user_id}:{project_id}"

def get_messages(user_id: str, project_id: str) -> List[dict]:
    return session_messages[session_key(user_id, project_id)]

def append_message(user_id: str, project_id: str, message: dict):
    session_messages[session_key(user_id, project_id)].append(message)

def clear_session(user_id: str, project_id: str):
    session_messages.pop(session_key(user_id, project_id), None)
