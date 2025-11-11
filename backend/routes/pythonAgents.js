/**
 * Python AI Service Integration
 * Bridges Node.js backend with Python AI service
 */

const express = require('express');
const router = express.Router();
const axios = require('axios');
const { auth, authorize } = require('../middleware/auth');

// Python AI service configuration
const PYTHON_AI_URL = process.env.PYTHON_AI_URL || 'http://localhost:8000';
const PYTHON_AI_KEY = process.env.BACKEND_API_KEY || 'dev-api-key-12345';

// Create axios instance for Python service
const pythonAI = axios.create({
    baseURL: PYTHON_AI_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': PYTHON_AI_KEY
    },
    timeout: 30000 // 30 seconds
});

// Error handler
const handlePythonError = (error, res) => {
    console.error('❌ Python AI Service Error:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
        return res.status(503).json({
            success: false,
            message: 'AI Service is not running. Please start the Python AI service.',
            error: 'Service unavailable'
        });
    }
    
    if (error.response) {
        return res.status(error.response.status).json({
            success: false,
            message: error.response.data.message || 'AI service error',
            error: error.response.data.error
        });
    }
    
    return res.status(500).json({
        success: false,
        message: 'Failed to communicate with AI service',
        error: error.message
    });
};

// ==================== HEALTH CHECK ====================

router.get('/health', async (req, res) => {
    try {
        const response = await pythonAI.get('/health');
        res.json({
            success: true,
            python_service: response.data,
            integration: 'active'
        });
    } catch (error) {
        handlePythonError(error, res);
    }
});

// ==================== CHATBOT ENDPOINTS ====================

router.post('/chat', auth, async (req, res) => {
    try {
        const { message, context, conversation_id } = req.body;
        
        if (!message) {
            return res.status(400).json({
                success: false,
                message: 'Message is required'
            });
        }
        
        console.log(`💬 Routing chat to Python AI: "${message.substring(0, 50)}..."`);
        
        const response = await pythonAI.post('/api/chat', {
            message,
            user_id: req.userId,
            context: context || {},
            conversation_id
        });
        
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

router.post('/chat/voice', auth, async (req, res) => {
    try {
        const { query, context } = req.body;
        
        if (!query) {
            return res.status(400).json({
                success: false,
                message: 'Voice query is required'
            });
        }
        
        console.log(`🎤 Routing voice query to Python AI: "${query.substring(0, 50)}..."`);
        
        const response = await pythonAI.post('/api/chat/voice', {
            query,
            user_id: req.userId,
            context: context || {}
        });
        
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

router.delete('/chat/history', auth, async (req, res) => {
    try {
        const response = await pythonAI.delete(`/api/chat/history/${req.userId}`);
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

// ==================== STUDENT AGENT ENDPOINTS ====================

router.post('/agents/student/study-planner', auth, async (req, res) => {
    try {
        const { query, context } = req.body;
        
        if (!query) {
            return res.status(400).json({
                success: false,
                message: 'Query is required'
            });
        }
        
        console.log(`📚 Study Planner Agent: "${query.substring(0, 50)}..."`);
        
        const response = await pythonAI.post('/api/agents/student/study-planner', {
            query,
            user_id: req.userId,
            context: context || {}
        });
        
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

router.post('/agents/student/assignment-manager', auth, async (req, res) => {
    try {
        const { query, context } = req.body;
        
        if (!query) {
            return res.status(400).json({
                success: false,
                message: 'Query is required'
            });
        }
        
        console.log(`📝 Assignment Manager Agent: "${query.substring(0, 50)}..."`);
        
        const response = await pythonAI.post('/api/agents/student/assignment-manager', {
            query,
            user_id: req.userId,
            context: context || {}
        });
        
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

// ==================== ADMIN AGENT ENDPOINTS ====================

router.post('/agents/admin/report-generator', auth, authorize('admin'), async (req, res) => {
    try {
        const { query, context } = req.body;
        
        if (!query) {
            return res.status(400).json({
                success: false,
                message: 'Query is required'
            });
        }
        
        console.log(`📊 Report Generator Agent: "${query.substring(0, 50)}..."`);
        
        const response = await pythonAI.post('/api/agents/admin/report-generator', {
            query,
            user_id: req.userId,
            context: context || {}
        });
        
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

router.post('/agents/admin/helpdesk-manager', auth, authorize('admin'), async (req, res) => {
    try {
        const { query, context } = req.body;
        
        if (!query) {
            return res.status(400).json({
                success: false,
                message: 'Query is required'
            });
        }
        
        console.log(`🎫 Helpdesk Manager Agent: "${query.substring(0, 50)}..."`);
        
        const response = await pythonAI.post('/api/agents/admin/helpdesk-manager', {
            query,
            user_id: req.userId,
            context: context || {}
        });
        
        res.json(response.data);
    } catch (error) {
        handlePythonError(error, res);
    }
});

// ==================== TEST ENDPOINTS ====================

router.get('/test/agents', auth, async (req, res) => {
    try {
        const response = await pythonAI.get('/api/test/agents');
        res.json({
            success: true,
            message: 'All agents are operational',
            agents: response.data.agents,
            integration: 'Node.js <-> Python connection established'
        });
    } catch (error) {
        handlePythonError(error, res);
    }
});

module.exports = router;
