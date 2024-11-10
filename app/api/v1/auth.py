
# app/api/v1/auth.py
from fastapi import APIRouter
from app.core.auth import create_test_token

router = APIRouter()

@router.post("/test-token")
async def get_test_token(user_id: str):
    """Development endpoint to get test tokens"""
    token = create_test_token(user_id)
    return {"access_token": token, "token_type": "bearer"}