from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import BaseModel

class Article(BaseModel):
    __tablename__ = "articles"

    articleid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userid = Column(String, ForeignKey("users.userid"), nullable=False)
    # postId = Column(UUID(as_uuid=True), nullable=False)
    
    title = Column(Text, nullable=False)
    elements = Column(JSONB, nullable=False)
    elements_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="articles")
    
    def __repr__(self):
        return f"<Article {self.post_id}>"