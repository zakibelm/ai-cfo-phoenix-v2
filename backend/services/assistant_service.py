"""
AI Assistant Service
Provides intelligent support using RAG on documentation
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
import os

from services.preembedded_rag_service import PreEmbeddedRAGService

logger = logging.getLogger(__name__)


class AssistantService:
    """
    AI Assistant for user support and prompt enhancement
    Uses RAG on documentation to provide contextual help
    """
    
    def __init__(self):
        self.rag_service = PreEmbeddedRAGService()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Fast and cost-effective for chat
        
        # System prompt for the assistant
        self.system_prompt = """Tu es l'assistant IA de la plateforme AI CFO Suite Phoenix, un expert technique bienveillant et pédagogue.

**Ton rôle :**
1. Fournir un support technique précis et contextualisé aux utilisateurs
2. Répondre aux questions sur l'utilisation de la plateforme
3. Améliorer les prompts des utilisateurs quand ils sont mal formulés
4. Suggérer des fonctionnalités pertinentes selon le contexte
5. Guider les utilisateurs étape par étape dans leurs tâches

**Ton comportement :**
- Toujours répondre en français de manière claire et concise
- Utiliser les informations de la documentation fournie dans le contexte
- Si tu détectes qu'un prompt utilisateur est mal formulé, propose une version améliorée
- Être proactif : suggère des fonctionnalités ou des bonnes pratiques
- Rester professionnel mais chaleureux
- Si tu ne sais pas, dis-le honnêtement et propose des alternatives

**Format de réponse :**
- Utilise le markdown pour structurer tes réponses
- Mets en évidence les points importants
- Fournis des exemples concrets quand c'est pertinent
- Si tu améliores un prompt, explique pourquoi

**Documentation disponible :**
Tu as accès à la documentation complète de la plateforme (README, guides, évaluation experte, etc.) via le contexte fourni."""

    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in the conversation
            user_context: Additional context (current page, user role, etc.)
        
        Returns:
            Response with message, enhanced prompt if applicable, and suggestions
        """
        try:
            # 1. Retrieve relevant documentation using RAG
            docs_context = await self._get_documentation_context(user_message)
            
            # 2. Detect if prompt needs enhancement
            needs_enhancement = self._detect_prompt_issues(user_message)
            
            # 3. Build messages for LLM
            messages = self._build_messages(
                user_message,
                docs_context,
                conversation_history,
                user_context
            )
            
            # 4. Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            assistant_message = response.choices[0].message.content
            
            # 5. Extract enhanced prompt if suggested
            enhanced_prompt = None
            if needs_enhancement:
                enhanced_prompt = self._extract_enhanced_prompt(assistant_message)
            
            # 6. Generate suggestions
            suggestions = self._generate_suggestions(user_message, user_context)
            
            return {
                "message": assistant_message,
                "enhanced_prompt": enhanced_prompt,
                "suggestions": suggestions,
                "timestamp": datetime.utcnow().isoformat(),
                "sources": docs_context.get("sources", [])
            }
        
        except Exception as e:
            logger.error(f"Assistant chat error: {str(e)}")
            return {
                "message": "Désolé, je rencontre un problème technique. Pouvez-vous reformuler votre question ?",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_documentation_context(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant documentation using RAG"""
        try:
            # Query the documentation collection
            results = self.rag_service.query(
                query_text=query,
                collection_name="documentation",
                top_k=3
            )
            
            if not results:
                return {"context": "", "sources": []}
            
            # Build context from results
            context_parts = []
            sources = []
            
            for i, result in enumerate(results, 1):
                context_parts.append(f"[Document {i}]\n{result['text']}\n")
                sources.append({
                    "filename": result.get("filename", "Unknown"),
                    "score": result.get("score", 0)
                })
            
            return {
                "context": "\n".join(context_parts),
                "sources": sources
            }
        
        except Exception as e:
            logger.warning(f"Could not retrieve documentation context: {str(e)}")
            return {"context": "", "sources": []}
    
    def _detect_prompt_issues(self, message: str) -> bool:
        """Detect if user prompt might need enhancement"""
        # Simple heuristics
        issues = [
            len(message) < 10,  # Too short
            message.count(" ") < 2,  # Too few words
            not any(c in message for c in "?!."),  # No punctuation
            message.isupper(),  # All caps
        ]
        return any(issues)
    
    def _build_messages(
        self,
        user_message: str,
        docs_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]],
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Build messages array for LLM"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add documentation context if available
        if docs_context.get("context"):
            context_message = f"""**Documentation pertinente :**

{docs_context['context']}

---

Utilise ces informations pour répondre à l'utilisateur de manière précise."""
            messages.append({"role": "system", "content": context_message})
        
        # Add user context if available
        if user_context:
            context_info = f"**Contexte utilisateur :** Page actuelle: {user_context.get('current_page', 'Unknown')}, Rôle: {user_context.get('role', 'user')}"
            messages.append({"role": "system", "content": context_info})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Keep last 6 messages
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _extract_enhanced_prompt(self, assistant_message: str) -> Optional[str]:
        """Extract enhanced prompt from assistant response if present"""
        # Look for patterns like "Voici une meilleure formulation :" or "Je suggère :"
        markers = [
            "meilleure formulation",
            "je suggère",
            "reformulation",
            "version améliorée"
        ]
        
        for marker in markers:
            if marker in assistant_message.lower():
                # Try to extract the enhanced prompt (simple heuristic)
                lines = assistant_message.split("\n")
                for i, line in enumerate(lines):
                    if marker in line.lower() and i + 1 < len(lines):
                        # Return next non-empty line
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip():
                                return lines[j].strip().strip('"').strip("'")
        
        return None
    
    def _generate_suggestions(
        self,
        user_message: str,
        user_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        # Context-based suggestions
        if user_context:
            page = user_context.get("current_page", "").lower()
            
            if "document" in page:
                suggestions.append("Comment téléverser un document ?")
                suggestions.append("Quels formats de fichiers sont supportés ?")
            elif "dashboard" in page:
                suggestions.append("Comment interpréter les KPIs ?")
                suggestions.append("Que signifie 'Agents Actifs' ?")
            elif "playground" in page:
                suggestions.append("Comment formuler une bonne question ?")
                suggestions.append("Quels agents sont disponibles ?")
        
        # Keyword-based suggestions
        keywords = user_message.lower()
        if "agent" in keywords:
            suggestions.append("Quels sont les différents types d'agents ?")
        if "document" in keywords or "fichier" in keywords:
            suggestions.append("Comment gérer mes documents ?")
        if "erreur" in keywords or "problème" in keywords:
            suggestions.append("Voir les problèmes courants et solutions")
        
        return suggestions[:3]  # Return max 3 suggestions


# Global instance
assistant_service = AssistantService()

