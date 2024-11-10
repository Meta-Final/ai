
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

class ChatMessage(BaseModel):
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class FunctionCall(BaseModel):
    name: str
    result: Any

class ChatResponse(BaseModel):
    message: str
    function_call: Optional[FunctionCall] = None

class ChatHistory(BaseModel):
    messages: List[ChatMessage]