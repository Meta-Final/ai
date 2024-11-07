
from ..function_registry import FunctionRegistry
from ..vector_store import VectorStore
from ..embedding import EmbeddingService
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.database import SessionLocal
from app.models import Article
from app.core.logging import logger
from app.core.exceptions import ArticleNotFoundError, ValidationError
from app.models import User

vector_store = VectorStore()
embedding_service = EmbeddingService()

async def check_article_consistency(article_id: UUID) -> None:
    """Check if article exists in both PostgreSQL and Qdrant"""
    db = SessionLocal()
    try:
        pg_article = db.query(Article).filter(Article.id == article_id).first()
        try:
            await vector_store.get_article(str(article_id))
            qdrant_exists = True
        except:
            qdrant_exists = False

        if pg_article and not qdrant_exists:
            embedding = await embedding_service.get_embedding(pg_article.content["text"])
            await vector_store.add_article(
                str(article_id),
                embedding,
                {
                    "title": pg_article.title,
                    "snippet": pg_article.content["text"][:200]
                }
            )
        elif not pg_article and qdrant_exists:
            await vector_store.delete_article(str(article_id))
    finally:
        db.close()

async def create_article(json_data: dict, user_id: UUID) -> Article:
    parsed_data = await parse_json_post(json_data)
    
    db = SessionLocal()
    try:
        # added to put username in article
        user = db.query(User).filter(User.id == user_id).first()
        article = Article(
            user_id=user_id,
            title=parsed_data["title"],
            # added to put username in article
            username=user.username,
            content_text=parsed_data["content_text"],
            content_json=parsed_data["content_json"]
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        # Create vector embedding
        embedding = await embedding_service.get_embedding(parsed_data["content_text"])
        await vector_store.add_article(
            str(article.id),
            embedding,
            {
                "title": parsed_data["title"],
                "snippet": parsed_data["content_text"][:200]
            }
        )

        return article
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {e}")
        raise
    finally:
        db.close()

async def update_article(article_id: UUID, json_data: dict, user_id: UUID) -> Article:
    parsed_data = await parse_json_post(json_data)
    
    db = SessionLocal()
    try:
        article = db.query(Article).filter(
            Article.id == article_id,
            Article.user_id == user_id
        ).first()
        
        if not article:
            raise ArticleNotFoundError(str(article_id))

        article.title = parsed_data["title"]
        article.content_text = parsed_data["content_text"]
        article.content_json = parsed_data["content_json"]

        db.commit()
        db.refresh(article)

        # Update vector embedding
        embedding = await embedding_service.get_embedding(parsed_data["content_text"])
        await vector_store.add_article(
            str(article.id),
            embedding,
            {
                "title": parsed_data["title"],
                "snippet": parsed_data["content_text"][:200]
            }
        )

        return article
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating article: {e}")
        raise
    finally:
        db.close()

async def delete_article(article_id: UUID, user_id: UUID):
    db = SessionLocal()
    try:
        article = db.query(Article).filter(
            Article.id == article_id,
            Article.user_id == user_id
        ).first()
        
        if not article:
            raise ArticleNotFoundError(str(article_id))

        db.delete(article)
        db.commit()
        await vector_store.delete_article(str(article_id))
        
        return {"message": "Article deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting article: {e}")
        raise
    finally:
        db.close()


@FunctionRegistry.register(
    name="search_articles",
    description="Search for articles using natural language query",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query in natural language"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["query"]
    }
)
async def search_articles(query: str, limit: int = 10) -> List[dict]:
    try:
        query_embedding = await embedding_service.get_embedding(query)
        results = await vector_store.search_articles(query_embedding, limit)
        
        return [
            {
                "id": result.id,
                "title": result.payload.get("title"),
                "snippet": result.payload.get("snippet"),
                "score": result.score
            }
            for result in results
        ]
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        raise


@FunctionRegistry.register(
    name="get_article",
    description="Retrieve a specific article by its ID",
    parameters={
        "type": "object",
        "properties": {
            "article_id": {
                "type": "string",
                "description": "UUID of the article to retrieve",
                "format": "uuid"
            }
        },
        "required": ["article_id"]
    }
)
async def get_article(article_id: UUID) -> Article:
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise ArticleNotFoundError(str(article_id))
        
        # await check_article_consistency(article_id)
        return article
    finally:
        db.close()
    
#     return article
async def parse_json_post(post_data: dict) -> dict:
    """Parse JSON data and extract title and content"""
    title = post_data["posts"][0]["postId"]
    
    # Collect all text contents
    text_contents = []
    for page in post_data["posts"][0]["pages"]:
        for element in page["elements"]:
            if element["type"] == 0 and element["content"]:
                text_contents.append(element["content"])
    
    combined_text = "\n".join(text_contents)
    
    return {
        "title": title,
        "content_text": combined_text,
        "content_json": post_data
    }