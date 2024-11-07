from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel

class ChatMessage(BaseModel):
    __tablename__ = "langchain_chat_history"

    session_id = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # 'human' or 'ai'