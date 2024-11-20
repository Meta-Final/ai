# app/core/permissions.py

from fastapi import HTTPException, status
from app.models import Article
from app.core.database import SessionLocal
from uuid import UUID

async def verify_article_ownership(articleid: UUID, userid: UUID) -> bool:
    """Verify if user is the owner of the article"""
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.articleid == articleid).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        if article.userid != userid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this article"
            )
            
        return True
    finally:
        db.close()