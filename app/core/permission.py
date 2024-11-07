# app/core/permissions.py

from fastapi import HTTPException, status
from app.models import Article
from app.core.database import SessionLocal
from uuid import UUID

async def verify_article_ownership(article_id: UUID, user_id: UUID) -> bool:
    """Verify if user is the owner of the article"""
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        if article.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this article"
            )
            
        return True
    finally:
        db.close()