"""
User History Models
Stores user conversation and query history
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class HistoryEntry(BaseModel):
    """Single history entry"""
    id: str
    user_id: str
    title: str
    type: str  # 'chat', 'query', 'analysis', 'document'
    content: dict
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_favorite: bool = False
    tags: List[str] = []


class HistoryCreate(BaseModel):
    """Create new history entry"""
    title: str
    type: str
    content: dict
    tags: List[str] = []


class HistoryUpdate(BaseModel):
    """Update existing history entry"""
    title: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None


class HistoryResponse(BaseModel):
    """History entry response"""
    id: str
    title: str
    type: str
    preview: str  # Short preview of content
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_favorite: bool
    tags: List[str]

