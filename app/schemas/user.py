from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        
class CurrentUser(User):
    """Used for authentication/current user context"""
    firebase_uid: str