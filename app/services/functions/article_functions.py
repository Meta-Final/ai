from ..function_registry import FunctionRegistry
from ..vector_store import VectorStore
from ..embedding import EmbeddingService
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from app.core.database import SessionLocal
from app.models import Article
from app.core.logging import logger
from app.core.exceptions import ArticleNotFoundError, ValidationError
from app.models import User

vector_store = VectorStore()
embedding_service = EmbeddingService()
    
async def create_article(userid: str, elements: list) -> Article:
    parsed_data = await parse_json_post(elements)
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.userid == userid).first()
        if not user:
            raise ValueError(f"User with userid {userid} not found")
        
        # Convert elements to JSON-serializable format
        elements_json = [element.dict() for element in elements]
        
        article = Article(
            articleid=uuid4(),
            userid=userid,
            title=parsed_data["title"],
            elements=elements_json,
            elements_text=parsed_data["content_text"],
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        # Create vector embedding
        embedding = await embedding_service.get_embedding(parsed_data["content_text"])
        await vector_store.add_article(
            str(article.articleid),
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

async def update_article(articleid: UUID, userid: UUID, elements: list) -> Article:
    parsed_data = await parse_json_post(elements)
    
    db = SessionLocal()
    try:
        article = db.query(Article).filter(
            Article.articleid == articleid,
            Article.userid == userid
        ).first()
        
        if not article:
            raise ArticleNotFoundError(str(articleid))

        article.title = parsed_data["title"]
        article.elements = elements
        article.elements_text = parsed_data["content_text"]

        db.commit()
        db.refresh(article)

        # Update vector embedding
        embedding = await embedding_service.get_embedding(parsed_data["content_text"])
        await vector_store.add_article(
            str(article.articleid),
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


async def delete_article(articleid: UUID, userid: UUID):
    db = SessionLocal()
    try:
        article = db.query(Article).filter(
            Article.articleid == articleid,
            Article.userid == userid
        ).first()
        
        if not article:
            raise ArticleNotFoundError(str(articleid))

        db.delete(article)
        db.commit()
        await vector_store.delete_article(str(articleid))
        
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
                "articleid": result.id,
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
            "articleid": {
                "type": "string",
                "description": "UUID of the article to retrieve",
                "format": "uuid"
            }
        },
        "required": ["articleid"]
    }
)
async def get_article(articleid: UUID) -> Article:
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.articleid == articleid).first()
        if not article:
            raise ArticleNotFoundError(str(articleid))
        
        return article
    finally:
        db.close()
    
async def parse_json_post(elements: list) -> dict:
    """Parse JSON data and extract title and content"""
    if not elements:
        raise ValueError("Elements list is empty")

    first_post = elements[0]
    title = first_post.postId
    
    # Collect all text contents
    text_contents = []
    for post in elements:
        for page in post.pages:
            for element in page.elements:
                if element.type == 0 and element.content:
                    text_contents.append(element.content)
    
    combined_text = "\n".join(text_contents)
    
    return {
        "title": title,
        "content_text": combined_text,
    }
