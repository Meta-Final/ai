from fastapi import APIRouter

api_router = APIRouter()

from . import chat, users, auth, articles, files
from . import trend

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(trend.router, prefix="/trend", tags=["trend"])