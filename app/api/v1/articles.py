from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.schemas.article import *
from app.services.functions import article_functions
from app.core.logging import logger
from app.schemas.user import User
from app.core.permission import verify_article_ownership
router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_articles(
    request: SearchArticleRequest,
    # current_user: User = Depends(get_current_user)
):
    results = await article_functions.search_articles(
        request.query,
        request.limit
    )
    return SearchResponse(results=results)

@router.post("/create", response_model=ArticleResponse)
async def create_article(
    request: CreateArticleRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        article = await article_functions.create_article(
            json_data=request.json_data,
            user_id=current_user.id
        )
        return ArticleResponse(
            id=article.id,
            user_id=article.user_id,
            title=article.title,
            username=article.username,
            content_text=article.content_text,
            content_json=article.content_json,
            created_at=article.created_at.isoformat()  # Convert datetime to string
        )
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create article"
        )

@router.post("/delete")
async def delete_article(
    request: DeleteArticleRequest,
    current_user: User = Depends(get_current_user)
):
    # Check ownership before deleting
    await verify_article_ownership(request.article_id, current_user.id)
    return await article_functions.delete_article(
        article_id=request.article_id,
        user_id=current_user.id
    )

@router.post("/update", response_model=ArticleResponse)
async def update_article(
    request: UpdateArticleRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_article_ownership(request.article_id, current_user.id)
        article = await article_functions.update_article(
            article_id=request.article_id,
            json_data=request.json_data,
            user_id=current_user.id
        )
        return ArticleResponse(
            id=article.id,
            user_id=article.user_id,
            title=article.title,
            username=article.username,
            content_text=article.content_text,
            content_json=article.content_json,
            created_at=article.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error updating article: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update article"
        )

@router.post("/get", response_model=ArticleResponse)
async def get_article(
    request: GetArticleRequest,
    # current_user: User = Depends(get_current_user)
):
    try:
        article = await article_functions.get_article(request.article_id)
        return ArticleResponse(
            id=article.id,
            user_id=article.user_id,
            title=article.title,
            username=article.username,
            content_text=article.content_text,
            content_json=article.content_json,
            created_at=article.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error retrieving article: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve article"
        )