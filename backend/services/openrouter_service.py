"""
OpenRouter Service - Multi-model LLM access with a single API key
Replaces Gemini SDK with OpenRouter for access to multiple AI models
"""

import logging
import os
from typing import List, Dict, Any, Optional
import requests
from core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API (multi-model access)"""
    
    # Available models through OpenRouter
    AVAILABLE_MODELS = {
        "gpt-4-turbo": {
            "id": "openai/gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "provider": "OpenAI",
            "context_length": 128000,
            "cost_per_1k_tokens": {"prompt": 0.01, "completion": 0.03}
        },
        "gpt-4": {
            "id": "openai/gpt-4",
            "name": "GPT-4",
            "provider": "OpenAI",
            "context_length": 8192,
            "cost_per_1k_tokens": {"prompt": 0.03, "completion": 0.06}
        },
        "gpt-3.5-turbo": {
            "id": "openai/gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "provider": "OpenAI",
            "context_length": 16385,
            "cost_per_1k_tokens": {"prompt": 0.0015, "completion": 0.002}
        },
        "claude-3-opus": {
            "id": "anthropic/claude-3-opus",
            "name": "Claude 3 Opus",
            "provider": "Anthropic",
            "context_length": 200000,
            "cost_per_1k_tokens": {"prompt": 0.015, "completion": 0.075}
        },
        "claude-3-sonnet": {
            "id": "anthropic/claude-3-sonnet",
            "name": "Claude 3 Sonnet",
            "provider": "Anthropic",
            "context_length": 200000,
            "cost_per_1k_tokens": {"prompt": 0.003, "completion": 0.015}
        },
        "claude-3-haiku": {
            "id": "anthropic/claude-3-haiku",
            "name": "Claude 3 Haiku",
            "provider": "Anthropic",
            "context_length": 200000,
            "cost_per_1k_tokens": {"prompt": 0.00025, "completion": 0.00125}
        },
        "gemini-pro": {
            "id": "google/gemini-pro",
            "name": "Gemini Pro",
            "provider": "Google",
            "context_length": 32768,
            "cost_per_1k_tokens": {"prompt": 0.000125, "completion": 0.000375}
        },
        "gemini-pro-vision": {
            "id": "google/gemini-pro-vision",
            "name": "Gemini Pro Vision",
            "provider": "Google",
            "context_length": 16384,
            "cost_per_1k_tokens": {"prompt": 0.000125, "completion": 0.000375}
        },
        "mixtral-8x7b": {
            "id": "mistralai/mixtral-8x7b-instruct",
            "name": "Mixtral 8x7B",
            "provider": "Mistral AI",
            "context_length": 32768,
            "cost_per_1k_tokens": {"prompt": 0.00027, "completion": 0.00027}
        },
        "llama-3-70b": {
            "id": "meta-llama/llama-3-70b-instruct",
            "name": "Llama 3 70B",
            "provider": "Meta",
            "context_length": 8192,
            "cost_per_1k_tokens": {"prompt": 0.00059, "completion": 0.00079}
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-4-turbo"):
        """
        Initialize OpenRouter service
        
        Args:
            api_key: OpenRouter API key (if None, uses OPENROUTER_API_KEY from env)
            default_model: Default model to use (key from AVAILABLE_MODELS)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = default_model
        
        # Validate default model
        if default_model not in self.AVAILABLE_MODELS:
            logger.warning(f"Unknown model {default_model}, falling back to gpt-4-turbo")
            self.default_model = "gpt-4-turbo"
        
        logger.info(f"OpenRouter service initialized with default model: {self.default_model}")
    
    def get_model_id(self, model_key: str) -> str:
        """Get OpenRouter model ID from model key"""
        if model_key in self.AVAILABLE_MODELS:
            return self.AVAILABLE_MODELS[model_key]["id"]
        return model_key  # Assume it's already a full model ID
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        return [
            {
                "key": key,
                **info
            }
            for key, info in self.AVAILABLE_MODELS.items()
        ]
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenRouter
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            model: Model key or ID (if None, uses default_model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API
        
        Returns:
            Dict with response, model used, tokens, cost
        """
        model_key = model or self.default_model
        model_id = self.get_model_id(model_key)
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.APP_URL or "http://localhost:3000",
            "X-Title": "AI CFO Suite Phoenix"
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            logger.info(f"Calling OpenRouter with model: {model_id}")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response
            message_content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            # Calculate cost
            model_info = self.AVAILABLE_MODELS.get(model_key, {})
            cost_info = model_info.get("cost_per_1k_tokens", {"prompt": 0, "completion": 0})
            
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            estimated_cost = (
                (prompt_tokens / 1000) * cost_info["prompt"] +
                (completion_tokens / 1000) * cost_info["completion"]
            )
            
            result = {
                "response": message_content,
                "model": model_id,
                "model_key": model_key,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": usage.get("total_tokens", prompt_tokens + completion_tokens)
                },
                "estimated_cost_usd": round(estimated_cost, 6),
                "finish_reason": data["choices"][0].get("finish_reason"),
                "raw_response": data
            }
            
            logger.info(
                f"OpenRouter response received: {completion_tokens} tokens, "
                f"cost: ${estimated_cost:.6f}"
            )
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise RuntimeError(f"Failed to generate response from OpenRouter: {str(e)}")
    
    def generate_with_context(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response with RAG context
        
        Args:
            query: User query
            context_documents: List of relevant documents from RAG
            system_prompt: System prompt
            model: Model to use
            **kwargs: Additional parameters
        
        Returns:
            Dict with response and metadata
        """
        # Build context from documents
        context_text = "\n\n".join([
            f"[Document {i+1}]\n{doc.get('text', '')}\nSource: {doc.get('metadata', {}).get('source', 'Unknown')}"
            for i, doc in enumerate(context_documents[:5])  # Limit to top 5
        ])
        
        # Build enhanced prompt
        enhanced_prompt = f"""Contexte documentaire :
{context_text}

Question de l'utilisateur :
{query}

Instructions :
- Réponds en te basant UNIQUEMENT sur le contexte fourni
- Cite les sources entre crochets [Document X]
- Si l'information n'est pas dans le contexte, indique-le clairement
- Sois précis, factuel et professionnel"""
        
        # Generate response
        result = self.generate_response(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
            model=model,
            **kwargs
        )
        
        # Add context metadata
        result["context_documents_used"] = len(context_documents)
        result["sources"] = [
            {
                "document_id": doc.get("id"),
                "source": doc.get("metadata", {}).get("source"),
                "score": doc.get("score", 0.0)
            }
            for doc in context_documents[:5]
        ]
        
        return result
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Multi-turn chat conversation
        
        Args:
            messages: List of messages with role and content
            model: Model to use
            **kwargs: Additional parameters
        
        Returns:
            Dict with response and metadata
        """
        model_key = model or self.default_model
        model_id = self.get_model_id(model_key)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.APP_URL or "http://localhost:3000",
            "X-Title": "AI CFO Suite Phoenix"
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            message_content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            return {
                "response": message_content,
                "model": model_id,
                "usage": usage,
                "finish_reason": data["choices"][0].get("finish_reason")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter chat error: {str(e)}")
            raise RuntimeError(f"Failed to complete chat: {str(e)}")


# Global instance
openrouter_service = OpenRouterService()
