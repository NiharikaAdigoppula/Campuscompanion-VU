"""
Voice Assistant with Natural Language Processing
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .intelligent_chatbot import IntelligentChatbot

class VoiceAssistant:
    """
    Voice assistant that processes voice queries
    Uses the intelligent chatbot as its brain
    """
    
    def __init__(self):
        self.chatbot = IntelligentChatbot()
        logger.info("🎤 Voice Assistant initialized")
    
    async def process_voice_query(self, 
                                  query: str, 
                                  user_id: str, 
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process voice query
        Voice queries are treated as high-priority, conversational interactions
        """
        try:
            logger.info(f"🎤 Voice query from user {user_id}: {query[:50]}...")
            
            # Add voice context
            voice_context = context or {}
            voice_context["input_type"] = "voice"
            voice_context["requires_concise_response"] = True
            
            # Process through intelligent chatbot
            result = await self.chatbot.process_message(
                message=query,
                user_id=user_id,
                context=voice_context
            )
            
            # Format for voice output (more concise)
            voice_response = self._format_for_voice(result.get("response", ""))
            
            return {
                "success": True,
                "response": voice_response,
                "actions_taken": result.get("actions_taken", []),
                "voice_enabled": True,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"❌ Voice assistant error: {str(e)}")
            return {
                "success": False,
                "response": "I'm sorry, I couldn't process your voice request. Please try again.",
                "voice_enabled": True,
                "timestamp": datetime.utcnow()
            }
    
    def _format_for_voice(self, text: str) -> str:
        """
        Format response for voice output
        - Remove excessive formatting
        - Keep it concise
        - Maintain natural flow
        """
        # Remove markdown formatting for voice
        text = text.replace("**", "")
        text = text.replace("##", "")
        text = text.replace("###", "")
        
        # Remove excessive bullet points for better voice flow
        text = text.replace("•", "")
        text = text.replace("-", "")
        
        # Limit length for voice (first 500 characters + summary)
        if len(text) > 500:
            text = text[:500] + "... Would you like more details?"
        
        return text
