
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService
from app.core.logging import logger
from langchain.schema import HumanMessage, AIMessage, SystemMessage

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    try:
        chat_service = ChatService(session_id=request.session_id)
        response = await chat_service.process_message(request.message)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        chat_service = ChatService(session_id=session_id)
        messages = await chat_service.get_context_messages(limit=10)  # Get last 10 messages
        return {
            "messages": [
                {
                    "role": "user" if isinstance(m, HumanMessage) else "assistant",
                    "content": m.content
                }
                for m in messages
            ]
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))