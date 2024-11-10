
from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# class ArticleBase(BaseModel):
#     json_data: dict = Field(..., description="JSON data containing post information")

# class CreateArticleRequest(ArticleBase):
#     pass
class CreateArticleRequest(BaseModel):
    json_data: dict = Field(..., description="JSON data containing post information")

class UpdateArticleRequest(BaseModel):
    article_id: UUID4
    json_data: dict = Field(..., description="JSON data containing post information")

class SearchArticleRequest(BaseModel):
    query: str
    # limit: Optional[int] = 10
    limit: int = Field(default=10, ge=1, le=100)

class DeleteArticleRequest(BaseModel):
    article_id: UUID4

class GetArticleRequest(BaseModel):
    article_id: UUID4




class ArticleResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    title: str
    username: str
    content_text: str
    content_json: dict
    created_at: str
    
    class Config:
        from_attributes = True

class SearchResult(BaseModel):
    id: UUID4
    title: str
    # username: str
    snippet: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]