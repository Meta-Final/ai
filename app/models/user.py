# app/models/user.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    # Primary key
    userid = Column(String, primary_key=True, unique=True, nullable=False)
    
    # Auth fields
    email = Column(String, unique=True, nullable=True)
    username = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    
    # Relationships
    articles = relationship("Article", back_populates="user", lazy="dynamic")