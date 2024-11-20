from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    userid: str
    username: str
    email: Optional[str] = None

    class Config:
        orm_mode = True

class User(BaseModel):
    userid: str
    username: str
    email: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True