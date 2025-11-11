"""
Base Agent class for all intelligent agents
Provides common functionality for AI-powered agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import openai
import google.generativeai as genai
from anthropic import Anthropic

from config import settings
from database.mongodb_client import mongodb_client

class BaseAgent(ABC):
    """Base class for all agents with AI capabilities"""
    
    def __init__(self, agent_name: str, agent_description: str):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.ai_client = None
        self.ai_type = None
        
        # Initialize AI client
        self._initialize_ai_client()
        
        logger.info(f"🤖 {agent_name} initialized with {self.ai_type or 'rule-based'} AI")
    
    def _initialize_ai_client(self):
        """Initialize available AI client"""
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.ai_client = openai
            self.ai_type = "openai"
            logger.info(f"✅ {self.agent_name}: OpenAI initialized")
        elif settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.ai_client = genai
            self.ai_type = "gemini"
            logger.info(f"✅ {self.agent_name}: Gemini initialized")
        elif settings.ANTHROPIC_API_KEY:
            self.ai_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.ai_type = "anthropic"
            logger.info(f"✅ {self.agent_name}: Anthropic initialized")
        else:
            logger.warning(f"⚠️ {self.agent_name}: No AI API key found, using rule-based responses")
    
    async def generate_ai_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate AI response using available AI service"""
        try:
            if self.ai_type == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await openai.ChatCompletion.acreate(
                    model=settings.DEFAULT_AI_MODEL,
                    messages=messages,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                return response.choices[0].message.content
                
            elif self.ai_type == "gemini":
                model = genai.GenerativeModel('gemini-pro')
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = await model.generate_content_async(full_prompt)
                return response.text
                
            elif self.ai_type == "anthropic":
                response = await self.ai_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=settings.MAX_TOKENS,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                return self.get_fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"❌ AI generation error in {self.agent_name}: {str(e)}")
            return self.get_fallback_response(prompt)
    
    @abstractmethod
    def get_fallback_response(self, query: str) -> str:
        """Fallback response when AI is unavailable"""
        pass
    
    @abstractmethod
    async def process(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main processing method - must be implemented by subclasses"""
        pass
    
    async def fetch_user_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch user data from MongoDB"""
        try:
            users = mongodb_client.get_collection("users")
            user = await users.find_one({"_id": user_id})
            return user if user else {}
        except Exception as e:
            logger.error(f"Error fetching user data: {str(e)}")
            return {}
    
    async def fetch_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch user's enrolled courses"""
        try:
            user = await self.fetch_user_data(user_id)
            enrolled_course_ids = user.get("enrolledCourses", [])
            
            courses = mongodb_client.get_collection("courses")
            course_list = await courses.find({"_id": {"$in": enrolled_course_ids}}).to_list(length=100)
            return course_list
        except Exception as e:
            logger.error(f"Error fetching courses: {str(e)}")
            return []
    
    async def fetch_assignments(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch user's assignments"""
        try:
            assignments = mongodb_client.get_collection("assignments")
            assignment_list = await assignments.find({"userId": user_id}).to_list(length=100)
            return assignment_list
        except Exception as e:
            logger.error(f"Error fetching assignments: {str(e)}")
            return []
    
    async def fetch_materials(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch study materials"""
        try:
            import re
            materials = mongodb_client.get_collection("materials")

            # Debug: log types to catch truthiness/type issues
            logger.debug(f"fetch_materials: db_type={type(mongodb_client.db)}, collection_type={type(materials)}")

            if query:
                # Use $in with a compiled regex for tags (safer for array fields)
                regex = re.compile(re.escape(query), re.IGNORECASE)
                material_list = await materials.find({
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"description": {"$regex": query, "$options": "i"}},
                        {"tags": {"$in": [regex]}}
                    ]
                }).to_list(length=50)
            else:
                material_list = await materials.find().to_list(length=50)

            logger.debug(f"fetch_materials: found_count={len(material_list)}")
            return material_list
        except Exception as e:
            logger.error(f"Error fetching materials: {str(e)}")
            return []
    
    async def log_action(self, action_type: str, user_id: str, details: Dict[str, Any]):
        """Log agent actions for tracking"""
        try:
            logs = mongodb_client.get_collection("agent_logs")
            await logs.insert_one({
                "agent_name": self.agent_name,
                "action_type": action_type,
                "user_id": user_id,
                "details": details,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging action: {str(e)}")
    
    def format_response(self, 
                       response: str, 
                       actions: Optional[List[Dict[str, Any]]] = None,
                       analysis: Optional[Dict[str, Any]] = None,
                       data: Optional[Dict[str, Any]] = None,
                       recommendations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Format agent response"""
        return {
            "success": True,
            "agent_name": self.agent_name,
            "response": response,
            "actions_performed": actions or [],
            "analysis": analysis,
            "data": data,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow()
        }
