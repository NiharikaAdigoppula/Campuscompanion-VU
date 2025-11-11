# CampusCompanion Python AI Service

Intelligent AI service with action-capable agents for the CampusCompanion platform.

## 🌟 Features

### Student Agents
1. **Study Planner Agent** - Creates personalized study plans with AI analysis
2. **Assignment Manager Agent** - Manages assignments, deadlines, and provides help

### Admin Agents
1. **Report Generator Agent** - Generates comprehensive analytics and insights
2. **Helpdesk Manager Agent** - Intelligently manages support tickets

### Chatbot & Voice
- **Intelligent Chatbot** - ChatGPT-like conversational AI with memory
- **Voice Assistant** - Natural voice interaction support

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB (running on localhost:27017)
- At least one AI API key (OpenAI, Gemini, or Anthropic)

### Installation

1. **Create virtual environment:**
```powershell
cd python-ai-service
python -m venv venv
.\venv\Scripts\Activate
```

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Configure environment:**
```powershell
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Add at least one:
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# MongoDB connection (use same as main backend)
MONGODB_URI=mongodb://localhost:27017/campuscompanion
```

4. **Run the service:**
```powershell
python main.py
```

The service will start on `http://localhost:8000`

## 📡 API Endpoints

### Health Check
- `GET /` - Service status
- `GET /health` - Detailed health check
- `GET /api/test/agents` - Test all agents

### Chatbot
- `POST /api/chat` - Chat with AI (with conversation memory)
- `POST /api/chat/voice` - Voice assistant
- `DELETE /api/chat/history/{user_id}` - Clear chat history

### Student Agents
- `POST /api/agents/student/study-planner` - Create study plan
- `POST /api/agents/student/assignment-manager` - Manage assignments

### Admin Agents
- `POST /api/agents/admin/report-generator` - Generate reports
- `POST /api/agents/admin/helpdesk-manager` - Manage helpdesk

## 📋 API Request Examples

### Chat Request
```json
{
  "message": "Create a study plan for Data Structures",
  "user_id": "user_id_here",
  "context": {},
  "conversation_id": "optional"
}
```

### Agent Request
```json
{
  "query": "Show me all my pending assignments",
  "user_id": "user_id_here",
  "context": {}
}
```

## 🔧 Configuration

### AI Models
The service automatically uses the first available AI provider:
1. OpenAI (GPT-3.5-turbo by default)
2. Google Gemini
3. Anthropic Claude

If no API key is provided, it falls back to rule-based responses.

### Features
Enable/disable features in `.env`:
```env
ENABLE_CONVERSATION_MEMORY=true
ENABLE_AGENT_ACTIONS=true
ENABLE_VOICE_ASSISTANT=true
```

## 📊 Database Collections Used

- `users` - User information
- `courses` - Course data
- `assignments` - Student assignments
- `materials` - Study materials
- `events` - Campus events
- `conversations` - Chat history
- `agenticplans` - AI-generated plans
- `agent_logs` - Agent action logs

## 🔍 Troubleshooting

### Service won't start
- Check Python version: `python --version` (need 3.8+)
- Verify MongoDB is running
- Check if port 8000 is available

### Agents not working
- Verify at least one AI API key is set
- Check MongoDB connection
- Review logs in `logs/` directory

### Chatbot repeating responses
- The intelligent chatbot uses conversation memory
- Clear history: `DELETE /api/chat/history/{user_id}`
- Check `ENABLE_CONVERSATION_MEMORY` in `.env`

## 📝 Logs

Logs are stored in `logs/ai_service_*.log` with daily rotation.

## 🔒 Security

- API key validation for all endpoints
- Set `BACKEND_API_KEY` in `.env` for secure communication
- CORS configured for frontend (localhost:3000) and backend (localhost:5000)

## 🧪 Testing

Test the service:
```powershell
# Test health
curl http://localhost:8000/health

# Test agents
curl http://localhost:8000/api/test/agents
```

## 📚 Documentation

API documentation available at: `http://localhost:8000/docs` (FastAPI automatic docs)

## 🤝 Integration with Node.js Backend

The Python service integrates with your Node.js backend through REST API calls.
See `../backend/routes/pythonAgents.js` for integration code.

## ⚡ Performance

- Async/await for non-blocking operations
- Connection pooling for MongoDB
- Efficient conversation history management
- Caching support (Redis optional)

## 📈 Monitoring

Check logs for:
- Request processing times
- AI API usage
- Error rates
- Agent performance

## 🆘 Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Verify environment variables
3. Test database connection
4. Ensure AI API keys are valid

---

**Note:** This service is designed to run alongside your Node.js backend, not replace it. It handles AI-specific tasks while the Node.js backend manages routes, authentication, and other app logic.
