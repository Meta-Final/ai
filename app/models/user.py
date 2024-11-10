
# app/models/user.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class User(BaseModel):
    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Auth fields
    firebase_uid = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    username = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    
    # Relationships
    articles = relationship("Article", back_populates="user", lazy="dynamic")