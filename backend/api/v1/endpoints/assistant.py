"""
AI Assistant Endpoints
Chat interface for user support and prompt enhancement
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from services.assistant_service import assistant_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    user_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    enhanced_prompt: Optional[str] = None
    suggestions: List[str] = []
    timestamp: str
    sources: List[Dict[str, Any]] = []


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with the AI assistant
    
    The assistant uses RAG on documentation to provide contextual help,
    can enhance user prompts, and suggests relevant features.
    """
    try:
        # Convert conversation history to dict format
        history = None
        if request.conversation_history:
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Call assistant service
        response = await assistant_service.chat(
            user_message=request.message,
            conversation_history=history,
            user_context=request.user_context
        )
        
        return ChatResponse(**response)
    
    except Exception as e:
        logger.error(f"Assistant chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions(page: str = "dashboard"):
    """
    Get contextual suggestions based on current page
    """
    try:
        suggestions = assistant_service._generate_suggestions(
            user_message="",
            user_context={"current_page": page}
        )
        
        return {"suggestions": suggestions}
    
    except Exception as e:
        logger.error(f"Get suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-prompt")
async def enhance_prompt(prompt: str):
    """
    Enhance a user prompt to make it more effective
    """
    try:
        response = await assistant_service.chat(
            user_message=f"Améliore ce prompt pour qu'il soit plus clair et efficace : '{prompt}'",
            conversation_history=None,
            user_context={"task": "prompt_enhancement"}
        )
        
        return {
            "original": prompt,
            "enhanced": response.get("enhanced_prompt") or response.get("message"),
            "explanation": response.get("message")
        }
    
    except Exception as e:
        logger.error(f"Enhance prompt error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

