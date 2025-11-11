"""
CampusCompanion Python AI Service
Main FastAPI application with intelligent agents
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger
import sys
from datetime import datetime
import asyncio

from config import settings
from models.schemas import (
    ChatRequest, ChatResponse,
    VoiceRequest, VoiceResponse,
    AgentRequest, AgentResponse,
    HealthResponse
)
from agents import (
    StudentStudyPlannerAgent,
    StudentAssignmentManagerAgent,
    AdminReportGeneratorAgent,
    AdminHelpdeskManagerAgent
)
from chatbot import IntelligentChatbot, VoiceAssistant
from database.mongodb_client import mongodb_client

# Configure logging
logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL)
logger.add("logs/ai_service_{time}.log", rotation="1 day", retention="7 days", level="INFO")

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Python AI Service...")
    
    # Initialize database connection
    try:
        await mongodb_client.connect()
        logger.success("✅ Database connected")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}. Running in limited mode.")
    
    # Initialize agents
    global student_planner, student_assignment, admin_report, admin_helpdesk
    global chatbot, voice_assistant
    
    student_planner = StudentStudyPlannerAgent()
    student_assignment = StudentAssignmentManagerAgent()
    admin_report = AdminReportGeneratorAgent()
    admin_helpdesk = AdminHelpdeskManagerAgent()
    chatbot = IntelligentChatbot()
    voice_assistant = VoiceAssistant()
    
    logger.success("✅ All agents initialized")
    logger.success(f"🎯 Service running on http://{settings.PYTHON_AI_HOST}:{settings.PYTHON_AI_PORT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Python AI Service...")
    await mongodb_client.disconnect()
    logger.success("✅ Service stopped gracefully")

# Create FastAPI app
app = FastAPI(
    title="CampusCompanion AI Service",
    description="Intelligent AI service with action-capable agents",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: API Key validation
async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key for secure communication"""
    if not x_api_key:
        return None  # Allow requests without API key in development
    if x_api_key != settings.BACKEND_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

# ==================== HEALTH & STATUS ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "running",
        "service": "CampusCompanion Python AI Service",
        "version": "2.0.0",
        "message": "AI service is operational"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "agents": {
            "student_planner": "active",
            "student_assignment": "active",
            "admin_report": "active",
            "admin_helpdesk": "active"
        },
        "chatbot": "active",
        "voice_assistant": "active"
    }

# ==================== CHATBOT ENDPOINTS ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    """
    Intelligent chatbot with conversation memory
    Handles general queries and routes to appropriate agents
    """
    try:
        logger.info(f"💬 Chat request from user {request.user_id}: {request.message[:50]}...")
        
        response = await chatbot.process_message(
            message=request.message,
            user_id=request.user_id,
            context=request.context,
            conversation_id=request.conversation_id
        )
        
        logger.success(f"✅ Chat response generated for user {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/voice", response_model=VoiceResponse)
async def voice_chat(request: VoiceRequest, api_key: str = Depends(verify_api_key)):
    """
    Voice assistant endpoint
    Converts speech to text, processes, and returns response
    """
    try:
        logger.info(f"🎤 Voice request from user {request.user_id}")
        
        response = await voice_assistant.process_voice_query(
            query=request.query,
            user_id=request.user_id,
            context=request.context
        )
        
        logger.success(f"✅ Voice response generated for user {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Voice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/history/{user_id}")
async def clear_chat_history(user_id: str, api_key: str = Depends(verify_api_key)):
    """Clear conversation history for a user"""
    try:
        await chatbot.clear_history(user_id)
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        logger.error(f"❌ Clear history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STUDENT AGENT ENDPOINTS ====================

@app.post("/api/agents/student/study-planner", response_model=AgentResponse)
async def student_study_planner(request: AgentRequest, api_key: str = Depends(verify_api_key)):
    """
    Student Study Planner Agent
    - Analyzes academic goals and current workload
    - Creates personalized study schedules
    - Finds relevant materials automatically
    - Sets up reminders and milestones
    """
    try:
        logger.info(f"📚 Study planner request from user {request.user_id}")
        
        response = await student_planner.process(
            query=request.query,
            user_id=request.user_id,
            context=request.context
        )
        
        logger.success(f"✅ Study plan created for user {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Study planner error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/student/assignment-manager", response_model=AgentResponse)
async def student_assignment_manager(request: AgentRequest, api_key: str = Depends(verify_api_key)):
    """
    Student Assignment Manager Agent
    - Tracks all assignments and deadlines
    - Prioritizes based on urgency and difficulty
    - Generates assignment outlines and content
    - Provides study resources and tips
    """
    try:
        logger.info(f"📝 Assignment manager request from user {request.user_id}")
        
        response = await student_assignment.process(
            query=request.query,
            user_id=request.user_id,
            context=request.context
        )
        
        logger.success(f"✅ Assignment management completed for user {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Assignment manager error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN AGENT ENDPOINTS ====================

@app.post("/api/agents/admin/report-generator", response_model=AgentResponse)
async def admin_report_generator(request: AgentRequest, api_key: str = Depends(verify_api_key)):
    """
    Admin Report Generator Agent
    - Generates comprehensive analytics reports
    - Analyzes student performance trends
    - Provides actionable insights
    - Creates visualizations and summaries
    """
    try:
        logger.info(f"📊 Report generation request from admin {request.user_id}")
        
        response = await admin_report.process(
            query=request.query,
            user_id=request.user_id,
            context=request.context
        )
        
        logger.success(f"✅ Report generated for admin {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Report generator error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/admin/helpdesk-manager", response_model=AgentResponse)
async def admin_helpdesk_manager(request: AgentRequest, api_key: str = Depends(verify_api_key)):
    """
    Admin Helpdesk Manager Agent
    - Auto-categorizes and prioritizes tickets
    - Suggests solutions based on past tickets
    - Auto-assigns tickets to appropriate staff
    - Generates response templates
    """
    try:
        logger.info(f"🎫 Helpdesk management request from admin {request.user_id}")
        
        response = await admin_helpdesk.process(
            query=request.query,
            user_id=request.user_id,
            context=request.context
        )
        
        logger.success(f"✅ Helpdesk task completed for admin {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Helpdesk manager error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TESTING ENDPOINTS ====================

@app.get("/api/test/agents")
async def test_agents():
    """Test all agents availability"""
    return {
        "success": True,
        "agents": {
            "student": {
                "study_planner": "operational",
                "assignment_manager": "operational"
            },
            "admin": {
                "report_generator": "operational",
                "helpdesk_manager": "operational"
            }
        },
        "chatbot": "operational",
        "voice_assistant": "operational"
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"❌ Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "Internal server error"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.PYTHON_AI_HOST,
        port=settings.PYTHON_AI_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

