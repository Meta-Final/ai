from fastapi import Depends, HTTPException, status, Request
from app.models import User
from app.core.database import SessionLocal
from app.core.logging import logger

from fastapi import Depends, HTTPException, status, Request
from app.models import User
from app.core.database import SessionLocal
from app.core.logging import logger

from fastapi import Request, HTTPException, status
from app.core.database import SessionLocal
from app.models import User
from app.core.logging import logger

async def get_current_user(request: Request):
    logger.info("Received request to get current user")
    
    try:
        body = await request.json()
        logger.debug(f"Request body: {body}")
    except Exception as e:
        logger.error(f"Error parsing request body: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body"
        )
    
    userid = body.get("userid")
    if not userid:
        logger.warning("Missing userid in request body")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Firebase UID"
        )
    
    # Get user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.userid == userid).first()
        if user is None:
            logger.warning(f"User not found for userid: {userid}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found. Please create a user first."
            )
        logger.info(f"User found: {user.userid}")
        return user
    finally:
        db.close()
        logger.info("Database session closed")
