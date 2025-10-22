"""
History Service
Manages user conversation and query history
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.history import HistoryEntry, HistoryCreate, HistoryUpdate, HistoryResponse

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Service for managing user history
    
    Note: This is an in-memory implementation for demo purposes.
    In production, use a proper database (PostgreSQL, MongoDB, etc.)
    """
    
    def __init__(self):
        # In-memory storage: {user_id: [history_entries]}
        self.history_store: Dict[str, List[HistoryEntry]] = {}
    
    def create_entry(
        self,
        user_id: str,
        data: HistoryCreate
    ) -> HistoryEntry:
        """Create a new history entry"""
        entry = HistoryEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=data.title,
            type=data.type,
            content=data.content,
            created_at=datetime.utcnow(),
            tags=data.tags
        )
        
        if user_id not in self.history_store:
            self.history_store[user_id] = []
        
        self.history_store[user_id].insert(0, entry)  # Add at beginning
        
        # Keep only last 100 entries per user
        if len(self.history_store[user_id]) > 100:
            self.history_store[user_id] = self.history_store[user_id][:100]
        
        logger.info(f"Created history entry {entry.id} for user {user_id}")
        return entry
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        type_filter: Optional[str] = None,
        favorites_only: bool = False
    ) -> List[HistoryResponse]:
        """Get user's history with optional filters"""
        entries = self.history_store.get(user_id, [])
        
        # Apply filters
        if type_filter:
            entries = [e for e in entries if e.type == type_filter]
        
        if favorites_only:
            entries = [e for e in entries if e.is_favorite]
        
        # Limit results
        entries = entries[:limit]
        
        # Convert to response format
        return [self._to_response(entry) for entry in entries]
    
    def get_entry(
        self,
        user_id: str,
        entry_id: str
    ) -> Optional[HistoryEntry]:
        """Get a specific history entry"""
        entries = self.history_store.get(user_id, [])
        
        for entry in entries:
            if entry.id == entry_id:
                return entry
        
        return None
    
    def update_entry(
        self,
        user_id: str,
        entry_id: str,
        data: HistoryUpdate
    ) -> Optional[HistoryEntry]:
        """Update a history entry"""
        entries = self.history_store.get(user_id, [])
        
        for i, entry in enumerate(entries):
            if entry.id == entry_id:
                # Update fields
                if data.title is not None:
                    entry.title = data.title
                if data.is_favorite is not None:
                    entry.is_favorite = data.is_favorite
                if data.tags is not None:
                    entry.tags = data.tags
                
                entry.updated_at = datetime.utcnow()
                
                self.history_store[user_id][i] = entry
                logger.info(f"Updated history entry {entry_id} for user {user_id}")
                return entry
        
        return None
    
    def delete_entry(
        self,
        user_id: str,
        entry_id: str
    ) -> bool:
        """Delete a history entry"""
        entries = self.history_store.get(user_id, [])
        
        for i, entry in enumerate(entries):
            if entry.id == entry_id:
                del self.history_store[user_id][i]
                logger.info(f"Deleted history entry {entry_id} for user {user_id}")
                return True
        
        return False
    
    def clear_user_history(
        self,
        user_id: str,
        type_filter: Optional[str] = None
    ) -> int:
        """Clear user's history (optionally by type)"""
        if user_id not in self.history_store:
            return 0
        
        if type_filter:
            original_count = len(self.history_store[user_id])
            self.history_store[user_id] = [
                e for e in self.history_store[user_id]
                if e.type != type_filter
            ]
            deleted_count = original_count - len(self.history_store[user_id])
        else:
            deleted_count = len(self.history_store[user_id])
            self.history_store[user_id] = []
        
        logger.info(f"Cleared {deleted_count} history entries for user {user_id}")
        return deleted_count
    
    def _to_response(self, entry: HistoryEntry) -> HistoryResponse:
        """Convert HistoryEntry to HistoryResponse"""
        # Generate preview from content
        preview = self._generate_preview(entry.content, entry.type)
        
        return HistoryResponse(
            id=entry.id,
            title=entry.title,
            type=entry.type,
            preview=preview,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            is_favorite=entry.is_favorite,
            tags=entry.tags
        )
    
    def _generate_preview(self, content: dict, type: str) -> str:
        """Generate a short preview from content"""
        if type == 'chat':
            # Get first user message
            messages = content.get('messages', [])
            for msg in messages:
                if msg.get('role') == 'user':
                    text = msg.get('content', '')
                    return text[:100] + '...' if len(text) > 100 else text
        
        elif type == 'query':
            query = content.get('query', '')
            return query[:100] + '...' if len(query) > 100 else query
        
        elif type == 'analysis':
            result = content.get('result', '')
            return result[:100] + '...' if len(result) > 100 else result
        
        elif type == 'document':
            doc_name = content.get('document_name', 'Document')
            return f"Analyse de {doc_name}"
        
        return "Aucun aperçu disponible"


# Global instance
history_service = HistoryService()

