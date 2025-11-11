"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# ==================== CHAT SCHEMAS ====================

class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for continuity")

class ChatResponse(BaseModel):
    """Chat response schema"""
    success: bool = Field(True, description="Success status")
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Response context")
    actions_taken: Optional[List[str]] = Field(default=None, description="Actions performed by AI")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==================== VOICE SCHEMAS ====================

class VoiceRequest(BaseModel):
    """Voice assistant request schema"""
    query: str = Field(..., description="Voice query text")
    user_id: str = Field(..., description="User ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    language: Optional[str] = Field(default="en", description="Language code")

class VoiceResponse(BaseModel):
    """Voice assistant response schema"""
    success: bool = Field(True, description="Success status")
    response: str = Field(..., description="Voice response text")
    actions_taken: Optional[List[str]] = Field(default=None, description="Actions performed")
    voice_enabled: bool = Field(True, description="Voice capability status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==================== AGENT SCHEMAS ====================

class AgentRequest(BaseModel):
    """Generic agent request schema"""
    query: str = Field(..., description="User query/command")
    user_id: str = Field(..., description="User ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    action_type: Optional[str] = Field(default=None, description="Specific action to perform")

class AgentResponse(BaseModel):
    """Generic agent response schema"""
    success: bool = Field(True, description="Success status")
    agent_name: str = Field(..., description="Agent that processed the request")
    response: str = Field(..., description="Agent response message")
    analysis: Optional[Dict[str, Any]] = Field(default=None, description="Analysis results")
    actions_performed: Optional[List[Dict[str, Any]]] = Field(default=None, description="Actions taken")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    recommendations: Optional[List[str]] = Field(default=None, description="AI recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==================== HEALTH SCHEMAS ====================

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    service: Optional[str] = Field(default=None, description="Service name")
    version: Optional[str] = Field(default=None, description="Service version")
    message: Optional[str] = Field(default=None, description="Status message")
    database: Optional[str] = Field(default=None, description="Database status")
    agents: Optional[Dict[str, Any]] = Field(default=None, description="Agent statuses")
    chatbot: Optional[str] = Field(default=None, description="Chatbot status")
    voice_assistant: Optional[str] = Field(default=None, description="Voice assistant status")

# ==================== DATA MODELS ====================

class ConversationMessage(BaseModel):
    """Conversation message model"""
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

class ConversationHistory(BaseModel):
    """Conversation history model"""
    user_id: str
    conversation_id: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
class AgentAction(BaseModel):
    """Agent action model"""
    action_type: str = Field(..., description="Type of action")
    parameters: Dict[str, Any] = Field(..., description="Action parameters")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Action result")
    success: bool = Field(True, description="Action success status")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
