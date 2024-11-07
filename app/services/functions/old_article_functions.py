
from ..function_registry import FunctionRegistry
from ..vector_store import VectorStore
from ..embedding import EmbeddingService
from app.core.database import SessionLocal
from app.core.exceptions import APIError, DatabaseError, ValidationError
from app.core.validators import validate_article_data
from app.models import Article
from app.core.logging import logger
from uuid import UUID
import json

vector_store = VectorStore()
embedding_service = EmbeddingService()

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
                "default": 5
            }
        },
        "required": ["query"]
    }
)
async def search_articles(query: str, limit: int = 5):
    try:
        # Generate embedding for query
        query_embedding = await embedding_service.get_embedding(query)
        
        # Search vector store
        results = await vector_store.search_articles(query_embedding, limit)
        
        # Format results
        formatted_results = [
            {
                "title": result.payload.get("title"),
                "snippet": result.payload.get("snippet"),
                "score": result.score
            }
            for result in results
        ]
        
        return formatted_results
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        raise
    
@FunctionRegistry.register(
    name="create_article",
    description="Create a new article with title and content",
    parameters={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the article"
            },
            "content": {
                "type": "string",
                "description": "Main content of the article"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for the article"
            }
        },
        "required": ["title", "content"]
    }
)
async def create_article(title: str, content: str, tags: list = None):
    try:
        # Validate input
        validate_article_data({
            "title": title,
            "content": content,
            "tags": tags
        })
        
        logger.info(f"Creating article with title: {title}")
        
        db = SessionLocal()
        try:
            # Create article in database
            article = Article(
                title=title,
                content={"text": content, "tags": tags or []},
                article_metadata={"tags": tags or []}
            )
            db.add(article)
            db.commit()
            db.refresh(article)
            
            # Generate embedding and store in vector database
            embedding = await embedding_service.get_embedding(content)
            await vector_store.add_article(
                str(article.id),
                embedding,
                {
                    "title": title,
                    "snippet": content[:200],
                    "tags": tags or []
                }
            )
            
            logger.info(f"Successfully created article: {article.id}")
            return {
                "id": str(article.id),
                "title": title,
                "message": "Article created successfully"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while creating article: {e}")
            raise DatabaseError(str(e))
            
        finally:
            db.close()
            
    except ValidationError as e:
        logger.error(f"Validation error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise APIError(
            status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"error": str(e)}
        )

@FunctionRegistry.register(
    name="get_article",
    description="Get full article content by ID",
    parameters={
        "type": "object",
        "properties": {
            "article_id": {
                "type": "string",
                "description": "ID of the article to retrieve"
            }
        },
        "required": ["article_id"]
    }
)
async def get_article(article_id: str):
    try:
        db = SessionLocal()
        article = db.query(Article).filter(Article.id == UUID(article_id)).first()
        if not article:
            return {"message": "Article not found"}
        
        return {
            "id": str(article.id),
            "title": article.title,
            "content": article.content["text"],
            "tags": article.content.get("tags", [])
        }
    except Exception as e:
        logger.error(f"Error getting article: {e}")
        raise
    finally:
        db.close()

@FunctionRegistry.register(
    name="update_article",
    description="Update an existing article",
    parameters={
        "type": "object",
        "properties": {
            "article_id": {
                "type": "string",
                "description": "ID of the article to update"
            },
            "title": {
                "type": "string",
                "description": "New title (optional)"
            },
            "content": {
                "type": "string",
                "description": "New content (optional)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "New tags (optional)"
            }
        },
        "required": ["article_id"]
    }
)
async def update_article(article_id: str, title: str = None, content: str = None, tags: list = None):
    try:
        db = SessionLocal()
        article = db.query(Article).filter(Article.id == UUID(article_id)).first()
        if not article:
            return {"message": "Article not found"}

        # Update fields if provided
        if title:
            article.title = title
        if content:
            article.content["text"] = content
        if tags:
            article.content["tags"] = tags
            article.article_metadata["tags"] = tags

        db.commit()
        db.refresh(article)

        # Update vector store if content changed
        if content:
            embedding = await embedding_service.get_embedding(content)
            await vector_store.add_article(
                article_id,
                embedding,
                {
                    "title": article.title,
                    "snippet": content[:200],
                    "tags": article.content.get("tags", [])
                }
            )

        return {
            "id": str(article.id),
            "message": "Article updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating article: {e}")
        raise
    finally:
        db.close()

@FunctionRegistry.register(
    name="delete_article",
    description="Delete an article by ID",
    parameters={
        "type": "object",
        "properties": {
            "article_id": {
                "type": "string",
                "description": "ID of the article to delete"
            }
        },
        "required": ["article_id"]
    }
)
async def delete_article(article_id: str):
    try:
        db = SessionLocal()
        article = db.query(Article).filter(Article.id == UUID(article_id)).first()
        if not article:
            return {"message": "Article not found"}

        # Delete from database
        db.delete(article)
        db.commit()

        # Delete from vector store
        await vector_store.delete_article(article_id)

        return {"message": "Article deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting article: {e}")
        raise
    finally:
        db.close()