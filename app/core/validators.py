from typing import Dict, Any
from .exceptions import ValidationError

def validate_article_data(data: Dict[str, Any]):
    if not data.get('title'):
        raise ValidationError("Title is required")
    
    if not data.get('content'):
        raise ValidationError("Content is required")
    
    if len(data['title']) > 255:
        raise ValidationError("Title is too long (max 255 characters)")
    
    if isinstance(data.get('tags'), list):
        for tag in data['tags']:
            if not isinstance(tag, str):
                raise ValidationError("Tags must be strings")