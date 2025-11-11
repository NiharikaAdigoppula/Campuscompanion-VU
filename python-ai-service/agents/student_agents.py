"""
Student-focused intelligent agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from .base_agent import BaseAgent
from database.mongodb_client import mongodb_client

class StudentStudyPlannerAgent(BaseAgent):
    """
    Intelligent Study Planner Agent for Students
    - Analyzes academic goals and current workload
    - Creates personalized study schedules
    - Finds and recommends relevant materials
    - Sets up reminders and milestones
    - Tracks progress and adjusts plans
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Study Planner Agent",
            agent_description="AI agent that creates personalized study plans and manages academic goals"
        )
    
    async def process(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process study planning request"""
        logger.info(f"📚 Study Planner processing request for user {user_id}")
        
        try:
            # Step 1: Gather user context
            user_context = await self._gather_user_context(user_id)
            
            # Step 2: Analyze the request
            analysis = await self._analyze_study_goal(query, user_context)
            
            # Step 3: Create study plan
            study_plan = await self._create_study_plan(query, user_context, analysis)
            
            # Step 4: Find relevant materials
            materials = await self._find_relevant_materials(query, study_plan)
            
            # Step 5: Save plan to database
            plan_id = await self._save_study_plan(user_id, study_plan, materials)
            
            # Step 6: Generate response
            response = await self._generate_response(study_plan, materials, analysis)
            
            # Log action
            await self.log_action("create_study_plan", user_id, {
                "plan_id": plan_id,
                "goal": query,
                "phases": len(study_plan.get("phases", []))
            })
            
            return self.format_response(
                response=response,
                actions=[
                    {"type": "study_plan_created", "plan_id": str(plan_id), "success": True},
                    {"type": "materials_found", "count": len(materials), "success": True}
                ],
                analysis=analysis,
                data={
                    "plan_id": str(plan_id),
                    "study_plan": study_plan,
                    "materials": materials[:5]  # Top 5 materials
                },
                recommendations=analysis.get("recommendations", [])
            )
            
        except Exception as e:
            logger.error(f"❌ Study Planner error: {str(e)}")
            return self.format_response(
                response=self.get_fallback_response(query),
                actions=[{"type": "error", "message": str(e), "success": False}]
            )
    
    async def _gather_user_context(self, user_id: str) -> Dict[str, Any]:
        """Gather comprehensive user context"""
        user = await self.fetch_user_data(user_id)
        courses = await self.fetch_courses(user_id)
        assignments = await self.fetch_assignments(user_id)
        
        return {
            "user": user,
            "courses": courses,
            "assignments": assignments,
            "total_courses": len(courses),
            "pending_assignments": len([a for a in assignments if a.get("status") == "pending"])
        }
    
    async def _analyze_study_goal(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze study goal using AI"""
        system_prompt = f"""You are an expert academic advisor. Analyze the student's study goal and provide insights.

Student Context:
- Department: {context['user'].get('department', 'N/A')}
- Year: {context['user'].get('year', 'N/A')}
- Enrolled Courses: {context['total_courses']}
- Pending Assignments: {context['pending_assignments']}

Provide analysis in JSON format:
{{
    "goal_type": "exam_prep|skill_learning|course_completion|general_study",
    "difficulty_level": "beginner|intermediate|advanced",
    "estimated_duration": "number of weeks",
    "key_topics": ["topic1", "topic2"],
    "prerequisites": ["prereq1", "prereq2"],
    "recommendations": ["rec1", "rec2"]
}}"""
        
        prompt = f"Student Goal: {query}\n\nAnalyze this study goal and provide structured guidance."
        
        ai_response = await self.generate_ai_response(prompt, system_prompt)
        
        try:
            # Extract JSON from response
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].strip()
            elif "{" in ai_response:
                json_str = ai_response[ai_response.index("{"):ai_response.rindex("}")+1]
            else:
                json_str = ai_response
            
            analysis = json.loads(json_str)
            return analysis
        except:
            # Fallback analysis
            return {
                "goal_type": "general_study",
                "difficulty_level": "intermediate",
                "estimated_duration": "2 weeks",
                "key_topics": [query],
                "prerequisites": [],
                "recommendations": [
                    "Start with fundamentals",
                    "Practice regularly",
                    "Review materials daily"
                ]
            }
    
    async def _create_study_plan(self, goal: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed study plan"""
        duration_weeks = int(analysis.get("estimated_duration", "2").split()[0])
        phases = []
        
        # Create phases (weeks)
        for week in range(duration_weeks):
            phase = {
                "name": f"Week {week + 1}",
                "order": week,
                "duration": "1 week",
                "start_date": (datetime.now() + timedelta(weeks=week)).isoformat(),
                "end_date": (datetime.now() + timedelta(weeks=week+1)).isoformat(),
                "tasks": []
            }
            
            # Create daily tasks
            for day in range(7):
                task = {
                    "title": f"Day {day + 1}: Study Session",
                    "description": f"Focus on {goal}",
                    "type": "study",
                    "estimated_hours": 2,
                    "deadline": (datetime.now() + timedelta(weeks=week, days=day)).isoformat(),
                    "status": "pending",
                    "priority": "high" if day < 3 else "medium"
                }
                phase["tasks"].append(task)
            
            # Add weekly assessment
            phase["tasks"].append({
                "title": f"Week {week + 1} Assessment",
                "description": f"Test your understanding of {goal}",
                "type": "assessment",
                "estimated_hours": 1,
                "deadline": phase["end_date"],
                "status": "pending",
                "priority": "high"
            })
            
            phases.append(phase)
        
        return {
            "goal": goal,
            "phases": phases,
            "total_duration": f"{duration_weeks} weeks",
            "key_topics": analysis.get("key_topics", []),
            "difficulty": analysis.get("difficulty_level", "intermediate"),
            "created_at": datetime.now().isoformat()
        }
    
    async def _find_relevant_materials(self, query: str, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relevant study materials"""
        materials = await self.fetch_materials(query)
        
        # Add relevance scoring
        for material in materials:
            material["relevance_score"] = 85  # Simplified scoring
            material["ai_recommended"] = True
        
        return materials
    
    async def _save_study_plan(self, user_id: str, plan: Dict[str, Any], materials: List[Dict[str, Any]]) -> str:
        """Save study plan to database"""
        try:
            plans_collection = mongodb_client.get_collection("agenticplans")
            
            plan_doc = {
                "userId": user_id,
                "planType": "study",
                "goal": plan["goal"],
                "status": "active",
                "plan": plan,
                "materials": materials,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = await plans_collection.insert_one(plan_doc)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error saving study plan: {str(e)}")
            return "temp_id"
    
    async def _generate_response(self, plan: Dict[str, Any], materials: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Generate human-readable response"""
        duration = plan.get("total_duration", "2 weeks")
        phases = len(plan.get("phases", []))
        
        response = f"""✅ **Study Plan Created Successfully!**

📚 **Goal:** {plan['goal']}
⏱️ **Duration:** {duration}
📊 **Difficulty:** {analysis.get('difficulty_level', 'intermediate').title()}

**📅 Plan Structure:**
• {phases} phases (weeks) of structured learning
• Daily study sessions (2 hours recommended)
• Weekly assessments to track progress

**🎯 Key Topics to Cover:**
{chr(10).join(f'• {topic}' for topic in analysis.get('key_topics', ['Core concepts'])[:5])}

**📖 Study Materials Found:** {len(materials)} resources
{chr(10).join(f'• {m.get("title", "Material")}' for m in materials[:3])}

**💡 AI Recommendations:**
{chr(10).join(f'• {rec}' for rec in analysis.get('recommendations', [])[:3])}

**🚀 Next Steps:**
1. Review your personalized plan in the dashboard
2. Access study materials from the resources section
3. Start with Week 1, Day 1 tasks
4. Track your progress regularly

Your study plan is ready! Let's achieve your academic goals together! 🎓"""
        
        return response
    
    def get_fallback_response(self, query: str) -> str:
        """Fallback response when AI is unavailable"""
        return f"""📚 I've created a basic study plan for: {query}

**Plan Overview:**
• Duration: 2 weeks
• Daily study sessions: 2 hours
• Weekly assessments
• Recommended materials will be provided

I'll help you stay on track with your studies! Check your dashboard for the complete plan."""


class StudentAssignmentManagerAgent(BaseAgent):
    """
    Intelligent Assignment Manager Agent for Students
    - Tracks all assignments and deadlines
    - Prioritizes based on urgency and difficulty
    - Generates assignment outlines and content
    - Provides study resources and tips
    - Manages submission tracking
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Assignment Manager Agent",
            agent_description="AI agent that manages assignments, deadlines, and provides academic assistance"
        )
    
    async def process(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process assignment management request"""
        logger.info(f"📝 Assignment Manager processing request for user {user_id}")
        
        try:
            # Detect action type
            action_type = self._detect_action_type(query)
            
            if action_type == "list_assignments":
                return await self._list_assignments(user_id, query)
            elif action_type == "generate_content":
                return await self._generate_assignment_content(user_id, query)
            elif action_type == "get_help":
                return await self._provide_assignment_help(user_id, query)
            else:
                return await self._general_assignment_guidance(user_id, query)
                
        except Exception as e:
            logger.error(f"❌ Assignment Manager error: {str(e)}")
            return self.format_response(
                response=self.get_fallback_response(query),
                actions=[{"type": "error", "message": str(e), "success": False}]
            )
    
    def _detect_action_type(self, query: str) -> str:
        """Detect what the user wants to do"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["list", "show", "what are", "my assignments"]):
            return "list_assignments"
        elif any(word in query_lower for word in ["generate", "create", "write", "help me with"]):
            return "generate_content"
        elif any(word in query_lower for word in ["help", "stuck", "how to", "guide"]):
            return "get_help"
        else:
            return "general"
    
    async def _list_assignments(self, user_id: str, query: str) -> Dict[str, Any]:
        """List and analyze user's assignments"""
        assignments = await self.fetch_assignments(user_id)
        
        if not assignments:
            return self.format_response(
                response="📝 You don't have any assignments yet. When assignments are added, I'll help you manage them!",
                data={"assignments": []}
            )
        
        # Analyze assignments
        pending = [a for a in assignments if a.get("status") == "pending"]
        completed = [a for a in assignments if a.get("status") == "completed"]
        overdue = [a for a in pending if datetime.fromisoformat(a.get("dueDate", datetime.now().isoformat())) < datetime.now()]
        
        # Prioritize assignments
        prioritized = sorted(pending, key=lambda x: (
            datetime.fromisoformat(x.get("dueDate", datetime.now().isoformat())),
            {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1)
        ))
        
        response = f"""📝 **Assignment Dashboard**

**📊 Overview:**
• Total Assignments: {len(assignments)}
• Pending: {len(pending)}
• Completed: {len(completed)}
• ⚠️ Overdue: {len(overdue)}

**🎯 Top Priority Assignments:**
{chr(10).join(f'{i+1}. **{a.get("title", "Assignment")}** - Due: {datetime.fromisoformat(a.get("dueDate", datetime.now().isoformat())).strftime("%b %d, %Y")} ({a.get("priority", "medium")} priority)' for i, a in enumerate(prioritized[:5]))}

**💡 Recommendations:**
• Focus on overdue assignments first
• Allocate time for high-priority tasks
• Break down large assignments into smaller tasks

Need help with any specific assignment? Just ask!"""
        
        return self.format_response(
            response=response,
            analysis={
                "total": len(assignments),
                "pending": len(pending),
                "completed": len(completed),
                "overdue": len(overdue)
            },
            data={"assignments": prioritized[:10]},
            actions=[{"type": "assignments_analyzed", "count": len(assignments), "success": True}]
        )
    
    async def _generate_assignment_content(self, user_id: str, query: str) -> Dict[str, Any]:
        """Generate assignment content using AI"""
        system_prompt = """You are an expert academic assistant. Help students create high-quality assignment content.

Provide:
1. Outline/structure
2. Key points to cover
3. Research suggestions
4. Writing tips"""
        
        ai_response = await self.generate_ai_response(query, system_prompt)
        
        response = f"""✍️ **Assignment Content Generation**

{ai_response}

**📚 Additional Resources:**
• Check the materials section for relevant resources
• Review course materials for background information
• Ensure proper citations and references

**💡 Pro Tips:**
• Start with an outline
• Break down into sections
• Review and revise before submission

Need more specific help? Let me know!"""
        
        return self.format_response(
            response=response,
            actions=[{"type": "content_generated", "success": True}]
        )
    
    async def _provide_assignment_help(self, user_id: str, query: str) -> Dict[str, Any]:
        """Provide help and guidance"""
        system_prompt = """You are a helpful academic tutor. Provide clear, step-by-step guidance for student queries."""
        
        ai_response = await self.generate_ai_response(query, system_prompt)
        
        return self.format_response(
            response=f"📖 **Assignment Help**\n\n{ai_response}",
            actions=[{"type": "help_provided", "success": True}]
        )
    
    async def _general_assignment_guidance(self, user_id: str, query: str) -> Dict[str, Any]:
        """General guidance"""
        assignments = await self.fetch_assignments(user_id)
        
        response = f"""📚 **Assignment Management**

I can help you with:
• 📋 List and track your assignments
• ✍️ Generate assignment content and outlines
• 📖 Provide research and writing guidance
• ⏰ Manage deadlines and priorities

You currently have **{len(assignments)} assignments**.

What would you like help with?"""
        
        return self.format_response(response=response)
    
    def get_fallback_response(self, query: str) -> str:
        """Fallback response"""
        return """📝 **Assignment Manager**

I'm here to help you manage your assignments! I can:
• Track all your assignments and deadlines
• Help you prioritize your work
• Generate content and outlines
• Provide study tips and resources

What do you need help with today?"""
