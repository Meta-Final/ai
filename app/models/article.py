from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import BaseModel

class Article(BaseModel):
    __tablename__ = "articles"

    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    username = Column(Text, nullable=False)
    # content = Column(JSON, nullable=False)
    content_text = Column(Text, nullable=True)  # For plain text content
    content_json = Column(JSONB, nullable=False)  # For original JSON data
    # Reserved for future metadata features (e.g., tags, categories)
    article_metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="articles")
    
    def __repr__(self):
        return f"<Article {self.title}>"