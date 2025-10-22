"""
History Endpoints
API for managing user history
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from models.history import HistoryCreate, HistoryUpdate, HistoryResponse, HistoryEntry
from services.history_service import history_service
from core.auth import get_current_user
from models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[HistoryResponse])
async def get_history(
    limit: int = 50,
    type: Optional[str] = None,
    favorites_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's history
    
    Query parameters:
    - limit: Maximum number of entries to return (default: 50)
    - type: Filter by type (chat, query, analysis, document)
    - favorites_only: Return only favorited entries
    """
    try:
        history = history_service.get_user_history(
            user_id=current_user.id,
            limit=limit,
            type_filter=type,
            favorites_only=favorites_only
        )
        return history
    
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=HistoryResponse)
async def create_history_entry(
    data: HistoryCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new history entry"""
    try:
        entry = history_service.create_entry(
            user_id=current_user.id,
            data=data
        )
        return history_service._to_response(entry)
    
    except Exception as e:
        logger.error(f"Create history entry error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=HistoryEntry)
async def get_history_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific history entry"""
    entry = history_service.get_entry(
        user_id=current_user.id,
        entry_id=entry_id
    )
    
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return entry


@router.patch("/{entry_id}", response_model=HistoryResponse)
async def update_history_entry(
    entry_id: str,
    data: HistoryUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a history entry"""
    entry = history_service.update_entry(
        user_id=current_user.id,
        entry_id=entry_id,
        data=data
    )
    
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return history_service._to_response(entry)


@router.delete("/{entry_id}")
async def delete_history_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a history entry"""
    success = history_service.delete_entry(
        user_id=current_user.id,
        entry_id=entry_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return {"message": "History entry deleted successfully"}


@router.delete("/")
async def clear_history(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Clear user's history
    
    Query parameters:
    - type: Optional type filter (chat, query, analysis, document)
    """
    deleted_count = history_service.clear_user_history(
        user_id=current_user.id,
        type_filter=type
    )
    
    return {
        "message": f"Deleted {deleted_count} history entries",
        "count": deleted_count
    }

