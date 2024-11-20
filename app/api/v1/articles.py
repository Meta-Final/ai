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
    request: SearchRequest,
    # current_user: User = Depends(get_current_user)
):
    try:
        results = await article_functions.search_articles(
            query=request.query,
            limit=request.limit
        )
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error searching articles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search articles")

@router.post("/create", response_model=ArticleResponse)
async def create_article(
    request: CreateArticleRequest,
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received create article request from user: {current_user.userid}")
    logger.debug(f"Request data: {request.json()}")
    
    try:
        article = await article_functions.create_article(
            userid=current_user.userid,
            elements=request.elements,
        )
        logger.info(f"Article created successfully: {article.articleid}")
        return ArticleResponse(
            articleid=article.articleid,
            userid=article.userid,
            title=article.title,
            elements=article.elements,
        )
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create article")

@router.post("/update", response_model=ArticleResponse)
async def update_article(
    request: UpdateArticleRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_article_ownership(request.articleid, current_user.userid)
        article = await article_functions.update_article(
            articleid=request.articleid,
            elements=request.elements,
            userid=current_user.userid
        )
        return ArticleResponse(
            articleid=article.articleid,
            userid=article.userid,
            title=article.title,
            elements=article.elements,
        )
    except Exception as e:
        logger.error(f"Error updating article: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update article")

@router.post("/delete")
async def delete_article(
    request: DeleteRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_article_ownership(request.articleid, current_user.userid)
        await article_functions.delete_article(
            articleid=request.articleid,
            userid=current_user.userid
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deleting article: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete article")

@router.post("/get", response_model=ArticleResponse)
async def get_article(
    request: GetArticleRequest,
    # current_user: User = Depends(get_current_user)
):
    try:
        article = await article_functions.get_article(request.articleid)
        return ArticleResponse(
            articleid=article.articleid,
            userid=article.userid,
            title=article.title,
            elements=article.elements,
            # # created_at=article.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error retrieving article: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve article")