from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel
from app.core.logging import logger

router = APIRouter()

@router.post("/create-user", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.debug(f"Received user creation request: {user}")
    db_user = UserModel(
        userid=user.userid,
        email=user.email,
        username=user.username
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        logger.debug(f"User created successfully: {db_user}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user