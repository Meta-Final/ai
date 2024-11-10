from fastapi import HTTPException
from typing import Any, Dict, Optional

class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail={
            "message": message,
            "error_code": error_code,
            "details": details
        })

class ArticleNotFoundError(APIError):
    def __init__(self, article_id: str):
        super().__init__(
            status_code=404,
            message=f"Article with ID {article_id} not found",
            error_code="ARTICLE_NOT_FOUND"
        )

class ValidationError(APIError):
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            status_code=400,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )

class DatabaseError(APIError):
    def __init__(self, message: str):
        super().__init__(
            status_code=500,
            message=f"Database error: {message}",
            error_code="DATABASE_ERROR"
        )