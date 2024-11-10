# # app/core/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User
from app.core.database import SessionLocal
from app.core.logging import logger
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify token and return current user.
    This is a development version - will be replaced with Firebase verification
    """
    try:
        # Verify token
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Get user from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.firebase_uid == payload["uid"]).first()
            if user is None:
                # For development: Create user if not exists
                user = User(
                    firebase_uid=payload["uid"],
                    email=payload.get("email"),
                    # username=f"user_{payload['uid'][:8]}"
                    username=f"{payload['uid'][:8]}"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        finally:
            db.close()
            
    except jwt.PyJWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

def create_test_token(user_id: str, email: str = None):
    """Create a test token (development only)"""
    payload = {
        "uid": user_id,
        "email": email or f"{user_id}@test.com",
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)