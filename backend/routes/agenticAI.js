const express = require('express');
const router = express.Router();
const { auth } = require('../middleware/auth');
const trueAgenticAI = require('../utils/trueAgenticAI');
const agenticAICore = require('../utils/agenticAICore');
const User = require('../models/User');
const Timetable = require('../models/Timetable');
const advancedAI = require('../utils/advancedAI');
const AgenticPlan = require('../models/AgenticPlan');
const AgenticTest = require('../models/AgenticTest');
const AgenticNotification = require('../models/AgenticNotification');

// ==================== PROFESSIONAL AGENTIC AI SYSTEM ====================

// Health check for TRUE agent system
router.get('/agent-status', auth, async (req, res) => {
  try {
    res.json({
      success: true,
      message: 'TRUE Agentic AI System is running',
      version: '2.0',
      features: {
        studyPlan: 'active',
        careerAdvice: 'active',
        examPrep: 'active',
        materialFinder: 'active',
        testGeneration: 'active',
        notifications: 'active'
      },
      models: {
        AgenticPlan: 'loaded',
        AgenticTest: 'loaded',
        AgenticNotification: 'loaded'
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Agent system check failed',
      error: error.message
    });
  }
});

// STEP 1: Understand User Goals - TRUE AGENT
router.post('/understand-goals', auth, async (req, res) => {
  try {
    console.log('🎯 [ROUTE] Received goal creation request');
    console.log('📝 [ROUTE] Request body:', req.body);
    console.log('👤 [ROUTE] User ID:', req.userId);
    
    const { goal } = req.body;
    
    if (!goal) {
      console.log('❌ [ROUTE] No goal provided');
      return res.status(400).json({
        success: false,
        message: 'Please provide your goal'
      });
    }

    console.log('🤖 [ROUTE] Creating plan with TRUE agent...');
    
    // Use TRUE Agentic AI to create a plan immediately
    const duration = goal.includes('day') ? goal.match(/\d+/)?.[0] + ' days' : '2 weeks';
    console.log('⏱️ [ROUTE] Duration:', duration);
    
    const result = await trueAgenticAI.generateStudyPlan(req.userId, goal, duration);
    
    console.log('✅ [ROUTE] Plan created successfully!');
    console.log('📊 [ROUTE] Plan ID:', result.planId);

    res.json({
      success: true,
      goalType: 'learning',
      clarifyingQuestions: [],
      analysis: result.plan.analysis,
      planId: result.planId,
      message: 'Goal analyzed and plan created!'
    });
  } catch (error) {
    console.error('❌ [ROUTE] Error in understand-goals:', error);
    console.error('❌ [ROUTE] Error stack:', error.stack);
    res.status(500).json({
      success: false,
      message: 'Failed to analyze your goal',
      error: error.message,
      details: error.stack
    });
  }
});

// STEP 2: Create Action Plan - TRUE AGENT
router.post('/create-plan', auth, async (req, res) => {
  try {
    const { goalDetails, userAnswers, goal } = req.body;
    
    // Create plan using TRUE agent
    const goalText = goal || goalDetails?.goal || 'Achieve academic success';
    const duration = goalDetails?.duration || '2 weeks';
    
    const result = await trueAgenticAI.generateStudyPlan(req.userId, goalText, duration);

    res.json({
      success: true,
      actionPlan: result.plan,
      planId: result.planId,
      agentStatus: result.agentStatus,
      actions: result.actions
    });
  } catch (error) {
    console.error('Create plan error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create action plan',
      error: error.message
    });
  }
});

// STEP 3: Execute Plan
router.post('/execute-plan', auth, async (req, res) => {
  try {
    const { taskId } = req.body;
    
    const result = await agenticAICore.executePlan(req.userId, taskId);

    res.json(result);
  } catch (error) {
    console.error('Execute plan error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to execute plan',
      error: error.message
    });
  }
});

// Get Current Plan
router.get('/my-plan', auth, async (req, res) => {
  try {
    const plan = agenticAICore.getUserPlan(req.userId);
    
    if (!plan) {
      return res.json({
        success: true,
        hasPlan: false,
        message: 'No active plan found. Create one to get started!'
      });
    }

    const progress = agenticAICore.calculateProgress(req.userId);

    res.json({
      success: true,
      hasPlan: true,
      plan,
      progress
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch plan'
    });
  }
});

// Complete Task
router.post('/complete-task', auth, async (req, res) => {
  try {
    const { taskId } = req.body;
    
    const success = agenticAICore.completeTask(req.userId, taskId);
    
    if (success) {
      const progress = agenticAICore.calculateProgress(req.userId);
      
      res.json({
        success: true,
        message: 'Task completed successfully!',
        progress
      });
    } else {
      res.json({
        success: false,
        message: 'Task already completed or not found'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to complete task'
    });
  }
});

// Get Task Automation Status
router.get('/automation-status', auth, async (req, res) => {
  try {
    const plan = agenticAICore.getUserPlan(req.userId);
    
    if (!plan || !plan.actionPlan) {
      return res.json({
        success: true,
        automatedTasks: [],
        pendingTasks: []
      });
    }

    res.json({
      success: true,
      automationPlan: plan.actionPlan.automationPlan,
      automatedTasks: plan.actionPlan.automationPlan?.automatedTasks || [],
      manualTasks: plan.actionPlan.automationPlan?.manualTasks || []
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch automation status'
    });
  }
});

// ==================== LEGACY ENDPOINTS (Keep for compatibility) ====================

// AI Study Plan Generator - TRUE AGENT
router.post('/study-plan', auth, async (req, res) => {
  try {
    const { topics, timeline } = req.body;
    
    const goal = topics || 'Complete enrolled courses';
    const duration = timeline || '2 weeks';
    
    // Use TRUE Agentic AI System
    const result = await trueAgenticAI.generateStudyPlan(req.userId, goal, duration);
    
    res.json(result);
  } catch (error) {
    console.error('Study plan error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to generate study plan',
      error: error.message
    });
  }
});

// AI Career Advisor - TRUE AGENT
router.post('/career-advice', auth, async (req, res) => {
  try {
    // Use TRUE Agentic AI System
    const result = await trueAgenticAI.generateCareerAdvice(req.userId);
    
    res.json(result);
  } catch (error) {
    console.error('Career advice error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get career advice',
      error: error.message
    });
  }
});

// AI Exam Preparation Coach
router.post('/exam-prep', auth, async (req, res) => {
  try {
    const { subject, examDate, topics } = req.body;
    
    const user = await User.findById(req.userId).select('name department year');
    const timetable = await Timetable.findOne({ user: req.userId })
      .populate('entries.course', 'code name');

    let query = '';
    
    if (subject && examDate) {
      query = `Create a comprehensive exam preparation plan for ${subject} exam on ${examDate}. Include:
1. Daily study schedule
2. Topic-wise breakdown
3. Practice strategies
4. Time management tips
5. Revision techniques
6. Mock test schedule`;
    } else if (timetable && timetable.entries.length > 0) {
      const courses = timetable.entries.map(e => e.course.name).join(', ');
      query = `Create an exam preparation strategy for my courses: ${courses}. Include study schedule, practice tips, and revision strategies.`;
    } else {
      query = `Create a general exam preparation strategy for ${user.department} student with effective study techniques and time management.`;
    }

    const examPrep = await advancedAI.chat(query, req.userId, { user });

    res.json({
      success: true,
      examPrep
    });
  } catch (error) {
    console.error('Exam prep error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to generate exam preparation plan',
      error: error.message
    });
  }
});

// AI Learning Path Creator
router.post('/learning-path', auth, async (req, res) => {
  try {
    const { goal, duration } = req.body;
    
    const user = await User.findById(req.userId).select('name department year');

    const query = goal 
      ? `Create a detailed learning path to achieve: ${goal}. Duration: ${duration || '3 months'}. Include milestones, resources, and timeline.`
      : `Create a personalized learning path for ${user.year} year ${user.department} student. Include:
1. Short-term goals (1-3 months)
2. Medium-term goals (3-6 months)
3. Long-term goals (6-12 months)
4. Recommended courses and resources
5. Skill development milestones
6. Project ideas
7. Certification paths`;

    const learningPath = await advancedAI.chat(query, req.userId, { user });

    res.json({
      success: true,
      learningPath
    });
  } catch (error) {
    console.error('Learning path error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create learning path',
      error: error.message
    });
  }
});

// Multi-Agent Collaboration
router.post('/collaborate', auth, async (req, res) => {
  try {
    const { query } = req.body;

    if (!query) {
      return res.status(400).json({
        success: false,
        message: 'Query is required'
      });
    }

    const user = await User.findById(req.userId).select('name department year');
    
    const context = {
      user: {
        name: user.name,
        department: user.department,
        year: user.year
      }
    };

    // Use agenticAICore for collaborative processing
    const result = await agenticAICore.collaborativeProcess(
      query,
      context,
      req.userId.toString()
    );

    res.json({
      success: true,
      result
    });
  } catch (error) {
    console.error('Collaborative process error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to process collaborative query',
      error: error.message
    });
  }
});

// Get AI recommendations
router.post('/recommendations', auth, async (req, res) => {
  try {
    const user = await User.findById(req.userId).select('name department year');
    const timetable = await Timetable.findOne({ user: req.userId })
      .populate('entries.course', 'name');

    const query = `Based on my profile (${user.department}, Year ${user.year}) and enrolled courses, provide:
1. Study tips specific to my courses
2. Time management recommendations
3. Career development suggestions
4. Skill improvement areas
5. Resource recommendations`;

    const context = {
      user,
      courses: timetable?.entries.map(e => e.course) || []
    };

    const recommendations = await advancedAI.chat(query, req.userId, context);

    res.json({
      success: true,
      recommendations
    });
  } catch (error) {
    console.error('Recommendations error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get recommendations',
      error: error.message
    });
  }
});

// ==================== NEW TRUE AGENT ENDPOINTS ====================

// Get user's active plans
router.get('/my-plans', auth, async (req, res) => {
  try {
    const plans = await trueAgenticAI.getUserPlans(req.userId, {
      status: req.query.status,
      type: req.query.type,
      limit: parseInt(req.query.limit) || 10
    });
    
    res.json({
      success: true,
      count: plans.length,
      plans
    });
  } catch (error) {
    console.error('Get plans error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch plans',
      error: error.message
    });
  }
});

// Get specific plan details
router.get('/plan/:planId', auth, async (req, res) => {
  try {
    const plan = await trueAgenticAI.getPlanById(req.params.planId);
    
    if (!plan) {
      return res.status(404).json({
        success: false,
        message: 'Plan not found'
      });
    }
    
    if (plan.userId.toString() !== req.userId.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    res.json({
      success: true,
      plan
    });
  } catch (error) {
    console.error('Get plan error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch plan',
      error: error.message
    });
  }
});

// Update task status
router.put('/plan/:planId/task/:phaseIndex/:taskIndex', auth, async (req, res) => {
  try {
    const { status } = req.body;
    const { planId, phaseIndex, taskIndex } = req.params;
    
    const plan = await trueAgenticAI.updateTaskStatus(
      planId,
      parseInt(phaseIndex),
      parseInt(taskIndex),
      status
    );
    
    res.json({
      success: true,
      message: 'Task updated successfully',
      plan
    });
  } catch (error) {
    console.error('Update task error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update task',
      error: error.message
    });
  }
});

// Get user notifications
router.get('/notifications', auth, async (req, res) => {
  try {
    const notifications = await AgenticNotification.getUserNotifications(req.userId, {
      unreadOnly: req.query.unreadOnly === 'true',
      type: req.query.type,
      limit: parseInt(req.query.limit) || 20
    });
    
    res.json({
      success: true,
      count: notifications.length,
      notifications
    });
  } catch (error) {
    console.error('Get notifications error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch notifications',
      error: error.message
    });
  }
});

// Mark notification as read
router.put('/notifications/:notificationId/read', auth, async (req, res) => {
  try {
    const notification = await AgenticNotification.findById(req.params.notificationId);
    
    if (!notification) {
      return res.status(404).json({
        success: false,
        message: 'Notification not found'
      });
    }
    
    notification.markAsRead();
    await notification.save();
    
    res.json({
      success: true,
      message: 'Notification marked as read'
    });
  } catch (error) {
    console.error('Mark notification error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update notification',
      error: error.message
    });
  }
});

// Get user's tests
router.get('/tests', auth, async (req, res) => {
  try {
    const tests = await AgenticTest.find({ userId: req.userId })
      .sort({ createdAt: -1 })
      .limit(parseInt(req.query.limit) || 10);
    
    res.json({
      success: true,
      count: tests.length,
      tests
    });
  } catch (error) {
    console.error('Get tests error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch tests',
      error: error.message
    });
  }
});

// Get specific test
router.get('/tests/:testId', auth, async (req, res) => {
  try {
    const test = await AgenticTest.findById(req.params.testId);
    
    if (!test) {
      return res.status(404).json({
        success: false,
        message: 'Test not found'
      });
    }
    
    if (test.userId.toString() !== req.userId.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    res.json({
      success: true,
      test
    });
  } catch (error) {
    console.error('Get test error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch test',
      error: error.message
    });
  }
});

// Submit test answers
router.post('/tests/:testId/submit', auth, async (req, res) => {
  try {
    const { answers } = req.body; // { questionIndex: userAnswer }
    const test = await AgenticTest.findById(req.params.testId);
    
    if (!test) {
      return res.status(404).json({
        success: false,
        message: 'Test not found'
      });
    }
    
    // Update answers and check correctness
    Object.entries(answers).forEach(([index, answer]) => {
      const question = test.questions[parseInt(index)];
      question.userAnswer = answer;
      question.isCorrect = question.correctAnswer === answer;
      question.marksObtained = question.isCorrect ? (question.marks || 1) : 0;
    });
    
    // Calculate results
    test.calculateResults();
    
    // Generate AI feedback
    await test.generateAIFeedback();
    
    await test.save();
    
    res.json({
      success: true,
      message: 'Test submitted successfully',
      results: test.results
    });
  } catch (error) {
    console.error('Submit test error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to submit test',
      error: error.message
    });
  }
});

module.exports = router;
