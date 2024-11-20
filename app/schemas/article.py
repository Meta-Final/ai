from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict
from datetime import datetime

class Position(BaseModel):
    x: float
    y: float
    z: float

class Scale(BaseModel):
    x: float
    y: float
    z: float

class Element(BaseModel):
    content: str
    type: int
    imageData: str
    position: Position
    scale: Scale
    fontSize: int
    fontFace: str
    isUnderlined: bool
    isStrikethrough: bool

class Page(BaseModel):
    pageId: int
    elements: List[Element]

class Post(BaseModel):
    postId: str
    pages: List[Page]

class Posts(BaseModel):
    posts: List[Post]



class Article(BaseModel):
    userid: str
    articleid: UUID4
    elements: List[Post]

class CreateArticleRequest(BaseModel):
    userid: str
    elements: List[Post]

class UpdateArticleRequest(BaseModel):
    userid: str
    articleid: UUID4
    elements: List[Post]

class DeleteRequest(BaseModel):
    userid: str
    articleid: UUID4

class GetArticleRequest(BaseModel):
    userid: str
    articleid: UUID4

class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=100)






class ArticleResponse(BaseModel):
    userid: str
    articleid: UUID4
    elements: List[Post]

    class Config:
        orm_mode = True

class SearchResult(BaseModel):
    articleid: UUID4
    title: str
    snippet: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]