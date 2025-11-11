"""
Intelligent Chatbot with Conversation Memory
Unlike simple chatbots, this maintains context and can take actions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from loguru import logger
import openai
import google.generativeai as genai
from anthropic import Anthropic

from config import settings
from database.mongodb_client import mongodb_client

class IntelligentChatbot:
    """
    Advanced chatbot with:
    - Conversation memory (doesn't repeat previous messages)
    - Context awareness
    - Action capabilities
    - Smart routing to agents
    """
    
    def __init__(self):
        self.ai_client = None
        self.ai_type = None
        self._initialize_ai()
        
        # Conversation storage
        self.conversations = {}
        
        logger.info("🤖 Intelligent Chatbot initialized")
    
    def _initialize_ai(self):
        """Initialize AI client"""
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.ai_client = openai
            self.ai_type = "openai"
            logger.info("✅ Chatbot: OpenAI initialized")
        elif settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.ai_client = genai
            self.ai_type = "gemini"
            logger.info("✅ Chatbot: Gemini initialized")
        elif settings.ANTHROPIC_API_KEY:
            self.ai_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.ai_type = "anthropic"
            logger.info("✅ Chatbot: Anthropic initialized")
        else:
            logger.warning("⚠️ Chatbot: No AI API configured, using rule-based responses")
    
    async def process_message(self, 
                             message: str, 
                             user_id: str, 
                             context: Optional[Dict[str, Any]] = None,
                             conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message with full context awareness
        """
        try:
            logger.info(f"💬 Processing message from user {user_id}: {message[:50]}...")
            
            # Get or create conversation
            conv_id = conversation_id or f"{user_id}_{int(datetime.now().timestamp())}"
            conversation_history = await self._get_conversation_history(user_id, conv_id)
            
            # Gather context
            full_context = await self._gather_context(user_id, context)
            
            # Detect if action is needed
            action_needed = await self._detect_action_intent(message)
            
            if action_needed:
                # Route to appropriate agent
                response_data = await self._route_to_agent(message, user_id, full_context)
                response_text = response_data.get("response", "Action completed!")
            else:
                # Generate conversational response
                response_text = await self._generate_conversational_response(
                    message, 
                    conversation_history, 
                    full_context
                )
            
            # Save to conversation history
            await self._save_to_history(user_id, conv_id, message, response_text)
            
            return {
                "success": True,
                "response": response_text,
                "conversation_id": conv_id,
                "context": full_context,
                "actions_taken": response_data.get("actions_performed", []) if action_needed else [],
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"❌ Chatbot error: {str(e)}")
            return {
                "success": False,
                "response": "I apologize, but I encountered an error. Please try again.",
                "conversation_id": conv_id if 'conv_id' in locals() else None,
                "timestamp": datetime.utcnow()
            }
    
    async def _get_conversation_history(self, user_id: str, conv_id: str) -> List[Dict[str, str]]:
        """Get conversation history from database"""
        try:
            if settings.ENABLE_CONVERSATION_MEMORY:
                conversations = mongodb_client.get_collection("conversations")
                conv = await conversations.find_one({
                    "user_id": user_id,
                    "conversation_id": conv_id
                })
                
                if conv:
                    return conv.get("messages", [])[-10:]  # Last 10 messages
            
            return []
        except Exception as e:
            logger.error(f"Error fetching conversation history: {str(e)}")
            return []
    
    async def _save_to_history(self, user_id: str, conv_id: str, message: str, response: str):
        """Save message to conversation history"""
        try:
            if settings.ENABLE_CONVERSATION_MEMORY:
                conversations = mongodb_client.get_collection("conversations")
                
                await conversations.update_one(
                    {"user_id": user_id, "conversation_id": conv_id},
                    {
                        "$push": {
                            "messages": {
                                "$each": [
                                    {"role": "user", "content": message, "timestamp": datetime.utcnow()},
                                    {"role": "assistant", "content": response, "timestamp": datetime.utcnow()}
                                ]
                            }
                        },
                        "$set": {"updated_at": datetime.utcnow()},
                        "$setOnInsert": {"created_at": datetime.utcnow()}
                    },
                    upsert=True
                )
        except Exception as e:
            logger.error(f"Error saving to history: {str(e)}")
    
    async def _gather_context(self, user_id: str, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Gather comprehensive context"""
        context = additional_context or {}
        
        try:
            # Get user info
            users = mongodb_client.get_collection("users")
            user = await users.find_one({"_id": user_id})
            
            if user:
                context["user"] = {
                    "name": user.get("name"),
                    "role": user.get("role"),
                    "department": user.get("department"),
                    "year": user.get("year")
                }
            
            # Get recent activity
            context["timestamp"] = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            
        except Exception as e:
            logger.error(f"Error gathering context: {str(e)}")
        
        return context
    
    async def _detect_action_intent(self, message: str) -> bool:
        """Detect if user wants an action to be performed"""
        action_keywords = [
            "create", "generate", "make", "show me", "find", "search",
            "enroll", "register", "add", "schedule", "plan",
            "list my", "what are my", "get my"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in action_keywords)
    
    async def _route_to_agent(self, message: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to appropriate agent based on intent"""
        message_lower = message.lower()
        
        # Import agents
        from agents.student_agents import StudentStudyPlannerAgent, StudentAssignmentManagerAgent
        
        if any(word in message_lower for word in ["study plan", "learning plan", "schedule"]):
            agent = StudentStudyPlannerAgent()
            return await agent.process(message, user_id, context)
        elif any(word in message_lower for word in ["assignment", "homework", "task"]):
            agent = StudentAssignmentManagerAgent()
            return await agent.process(message, user_id, context)
        else:
            # Default response
            return {
                "response": "I can help you with that! Could you provide more details?",
                "actions_performed": []
            }
    
    async def _generate_conversational_response(self, 
                                               message: str, 
                                               history: List[Dict[str, str]],
                                               context: Dict[str, Any]) -> str:
        """Generate contextual conversational response"""
        
        if not self.ai_client:
            return self._get_rule_based_response(message, context)
        
        try:
            # Build context-aware prompt
            system_prompt = f"""You are CampusCompanion AI, a helpful and friendly campus assistant.

Current Context:
- User: {context.get('user', {}).get('name', 'Student')}
- Role: {context.get('user', {}).get('role', 'student')}
- Time: {context.get('timestamp', 'now')}

Guidelines:
- Be conversational and natural (like ChatGPT)
- Don't repeat previous responses
- Provide helpful, accurate information
- If you don't know something, admit it
- Keep responses concise but informative
- Use emojis sparingly and appropriately"""

            if self.ai_type == "openai":
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history
                for msg in history[-6:]:  # Last 6 messages (3 exchanges)
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # Add current message
                messages.append({"role": "user", "content": message})
                
                response = await openai.ChatCompletion.acreate(
                    model=settings.DEFAULT_AI_MODEL,
                    messages=messages,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                
                return response.choices[0].message.content
            
            elif self.ai_type == "gemini":
                # Build prompt with history
                prompt = f"{system_prompt}\n\nConversation History:\n"
                for msg in history[-4:]:
                    prompt += f"{msg['role'].title()}: {msg['content']}\n"
                prompt += f"\nUser: {message}\nAssistant:"
                
                model = genai.GenerativeModel('gemini-pro')
                response = await model.generate_content_async(prompt)
                return response.text
            
            elif self.ai_type == "anthropic":
                messages = []
                for msg in history[-6:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                messages.append({"role": "user", "content": message})
                
                response = await self.ai_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=settings.MAX_TOKENS,
                    system=system_prompt,
                    messages=messages
                )
                
                return response.content[0].text
            
        except Exception as e:
            logger.error(f"AI response generation error: {str(e)}")
            return self._get_rule_based_response(message, context)
    
    def _get_rule_based_response(self, message: str, context: Dict[str, Any]) -> str:
        """Fallback rule-based responses"""
        message_lower = message.lower()
        
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        if any(greeting in message_lower for greeting in greetings):
            user_name = context.get('user', {}).get('name', 'there')
            return f"Hello {user_name}! 👋 How can I assist you today? I can help with courses, assignments, events, and more!"
        
        if "help" in message_lower:
            return """I'm here to help! I can assist you with:

📚 **Academic:** Study plans, assignments, course information
🎯 **Campus Life:** Events, navigation, facilities
📊 **Information:** Timetables, faculty details, materials
🤖 **AI Features:** Intelligent agents, analytics, recommendations

What would you like help with?"""
        
        if any(word in message_lower for word in ["course", "class", "subject"]):
            return "I can help you with course information, enrollment, and materials. What specific course information do you need?"
        
        if "event" in message_lower:
            return "Looking for campus events? I can show you upcoming events, help you register, and provide event details. What would you like to know?"
        
        # Default response
        return f"""I understand you're asking about: "{message}"

I can help you with various campus-related queries. Could you provide more specific details or try asking about:
• Courses and enrollment
• Study materials and resources
• Campus events and activities
• Your timetable and schedule
• Assignments and deadlines

What would you like to know more about?"""
    
    async def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        try:
            conversations = mongodb_client.get_collection("conversations")
            await conversations.delete_many({"user_id": user_id})
            logger.info(f"Cleared conversation history for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
