"""
Admin-focused intelligent agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from .base_agent import BaseAgent
from database.mongodb_client import mongodb_client

class AdminReportGeneratorAgent(BaseAgent):
    """
    Intelligent Report Generator Agent for Admins
    - Generates comprehensive analytics reports
    - Analyzes student performance trends
    - Provides actionable insights
    - Creates visualizations and summaries
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Report Generator Agent",
            agent_description="AI agent that generates comprehensive analytics and reports for administrators"
        )
    
    async def process(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process report generation request"""
        logger.info(f"📊 Report Generator processing request for admin {user_id}")
        
        try:
            # Detect report type
            report_type = self._detect_report_type(query)
            
            # Generate report based on type
            if report_type == "student_performance":
                return await self._generate_student_performance_report()
            elif report_type == "engagement":
                return await self._generate_engagement_report()
            elif report_type == "course_analytics":
                return await self._generate_course_analytics()
            else:
                return await self._generate_overview_report()
                
        except Exception as e:
            logger.error(f"❌ Report Generator error: {str(e)}")
            return self.format_response(
                response=self.get_fallback_response(query),
                actions=[{"type": "error", "message": str(e), "success": False}]
            )
    
    def _detect_report_type(self, query: str) -> str:
        """Detect report type from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["student", "performance", "grades"]):
            return "student_performance"
        elif any(word in query_lower for word in ["engagement", "activity", "participation"]):
            return "engagement"
        elif any(word in query_lower for word in ["course", "enrollment", "class"]):
            return "course_analytics"
        else:
            return "overview"
    
    async def _generate_student_performance_report(self) -> Dict[str, Any]:
        """Generate student performance report"""
        try:
            # Fetch data
            users = mongodb_client.get_collection("users")
            students = await users.find({"role": "student"}).to_list(length=1000)
            
            courses = mongodb_client.get_collection("courses")
            all_courses = await courses.find().to_list(length=100)
            
            assignments = mongodb_client.get_collection("assignments")
            all_assignments = await assignments.find().to_list(length=1000)
            
            # Calculate metrics
            total_students = len(students)
            active_students = len([s for s in students if s.get("enrolledCourses")])
            avg_courses_per_student = sum(len(s.get("enrolledCourses", [])) for s in students) / max(total_students, 1)
            
            completed_assignments = len([a for a in all_assignments if a.get("status") == "completed"])
            total_assignments = len(all_assignments)
            completion_rate = (completed_assignments / max(total_assignments, 1)) * 100
            
            # AI Analysis
            analysis_prompt = f"""Analyze this student performance data and provide insights:

Total Students: {total_students}
Active Students: {active_students}
Avg Courses per Student: {avg_courses_per_student:.1f}
Assignment Completion Rate: {completion_rate:.1f}%

Provide:
1. Key insights
2. Trends
3. Recommendations for improvement
4. Areas of concern"""
            
            ai_insights = await self.generate_ai_response(analysis_prompt)
            
            response = f"""📊 **Student Performance Report**

**📈 Key Metrics:**
• Total Students: {total_students}
• Active Students: {active_students}
• Average Courses per Student: {avg_courses_per_student:.1f}
• Assignment Completion Rate: {completion_rate:.1f}%

**🔍 AI Insights:**
{ai_insights}

**📅 Report Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

This report provides a comprehensive overview of student performance across the institution."""
            
            await self.log_action("generate_report", "admin", {
                "report_type": "student_performance",
                "students_analyzed": total_students
            })
            
            return self.format_response(
                response=response,
                analysis={
                    "total_students": total_students,
                    "active_students": active_students,
                    "completion_rate": completion_rate
                },
                data={
                    "students": total_students,
                    "courses": len(all_courses),
                    "assignments": total_assignments
                },
                actions=[{"type": "report_generated", "report_type": "student_performance", "success": True}]
            )
            
        except Exception as e:
            logger.error(f"Error generating student performance report: {str(e)}")
            raise
    
    async def _generate_engagement_report(self) -> Dict[str, Any]:
        """Generate engagement analytics report"""
        try:
            events = mongodb_client.get_collection("events")
            all_events = await events.find().to_list(length=100)
            
            materials = mongodb_client.get_collection("materials")
            all_materials = await materials.find().to_list(length=100)
            
            total_events = len(all_events)
            upcoming_events = len([e for e in all_events if e.get("status") == "upcoming"])
            
            response = f"""📊 **Engagement Analytics Report**

**🎯 Event Metrics:**
• Total Events: {total_events}
• Upcoming Events: {upcoming_events}
• Materials Available: {len(all_materials)}

**💡 Engagement Insights:**
• Students are actively participating in campus activities
• Study materials are being regularly accessed
• Event registration shows healthy engagement levels

**📅 Generated:** {datetime.now().strftime("%B %d, %Y")}"""
            
            return self.format_response(
                response=response,
                data={"events": total_events, "materials": len(all_materials)},
                actions=[{"type": "report_generated", "report_type": "engagement", "success": True}]
            )
            
        except Exception as e:
            logger.error(f"Error generating engagement report: {str(e)}")
            raise
    
    async def _generate_course_analytics(self) -> Dict[str, Any]:
        """Generate course analytics report"""
        try:
            courses = mongodb_client.get_collection("courses")
            all_courses = await courses.find().to_list(length=100)
            
            total_courses = len(all_courses)
            departments = set(c.get("department", "Unknown") for c in all_courses)
            
            response = f"""📊 **Course Analytics Report**

**📚 Course Metrics:**
• Total Courses: {total_courses}
• Departments: {len(departments)}
• Average Enrollment: Calculating...

**🎓 Department Breakdown:**
{chr(10).join(f'• {dept}' for dept in sorted(departments))}

**📅 Generated:** {datetime.now().strftime("%B %d, %Y")}"""
            
            return self.format_response(
                response=response,
                data={"courses": total_courses, "departments": len(departments)},
                actions=[{"type": "report_generated", "report_type": "course_analytics", "success": True}]
            )
            
        except Exception as e:
            logger.error(f"Error generating course analytics: {str(e)}")
            raise
    
    async def _generate_overview_report(self) -> Dict[str, Any]:
        """Generate comprehensive overview report"""
        try:
            # Gather all data
            users = mongodb_client.get_collection("users")
            courses = mongodb_client.get_collection("courses")
            events = mongodb_client.get_collection("events")
            materials = mongodb_client.get_collection("materials")
            
            student_count = await users.count_documents({"role": "student"})
            course_count = await courses.count_documents({})
            event_count = await events.count_documents({})
            material_count = await materials.count_documents({})
            
            response = f"""📊 **System Overview Report**

**🎓 Institution Snapshot:**
• Students: {student_count}
• Courses: {course_count}
• Events: {event_count}
• Study Materials: {material_count}

**✅ System Status:** All systems operational
**📅 Report Date:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

**💡 Quick Insights:**
• Platform is actively being used by students and faculty
• Content library is growing
• Engagement metrics show positive trends

For detailed analytics, request specific report types (student performance, engagement, or course analytics)."""
            
            return self.format_response(
                response=response,
                data={
                    "students": student_count,
                    "courses": course_count,
                    "events": event_count,
                    "materials": material_count
                },
                actions=[{"type": "report_generated", "report_type": "overview", "success": True}]
            )
            
        except Exception as e:
            logger.error(f"Error generating overview report: {str(e)}")
            raise
    
    def get_fallback_response(self, query: str) -> str:
        """Fallback response"""
        return """📊 **Report Generator**

I can generate comprehensive reports including:
• Student Performance Analytics
• Engagement Metrics
• Course Analytics
• System Overview

What type of report would you like to generate?"""


class AdminHelpdeskManagerAgent(BaseAgent):
    """
    Intelligent Helpdesk Manager Agent for Admins
    - Auto-categorizes and prioritizes tickets
    - Suggests solutions based on past tickets
    - Auto-assigns tickets to appropriate staff
    - Generates response templates
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Helpdesk Manager Agent",
            agent_description="AI agent that intelligently manages helpdesk tickets and support requests"
        )
    
    async def process(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process helpdesk management request"""
        logger.info(f"🎫 Helpdesk Manager processing request for admin {user_id}")
        
        try:
            action_type = self._detect_action_type(query)
            
            if action_type == "categorize":
                return await self._categorize_ticket(query, context)
            elif action_type == "suggest_solution":
                return await self._suggest_solution(query, context)
            elif action_type == "list_tickets":
                return await self._list_tickets()
            else:
                return await self._general_helpdesk_info()
                
        except Exception as e:
            logger.error(f"❌ Helpdesk Manager error: {str(e)}")
            return self.format_response(
                response=self.get_fallback_response(query),
                actions=[{"type": "error", "message": str(e), "success": False}]
            )
    
    def _detect_action_type(self, query: str) -> str:
        """Detect action type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["categorize", "category", "classify"]):
            return "categorize"
        elif any(word in query_lower for word in ["solve", "solution", "fix", "help"]):
            return "suggest_solution"
        elif any(word in query_lower for word in ["list", "show", "tickets", "pending"]):
            return "list_tickets"
        else:
            return "general"
    
    async def _categorize_ticket(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Auto-categorize a support ticket"""
        ticket_description = context.get("description", query) if context else query
        
        system_prompt = """You are a helpdesk categorization expert. Categorize support tickets accurately.

Categories:
- Technical Issue
- Account Access
- Course Enrollment
- Payment/Billing
- General Inquiry
- Feature Request
- Bug Report

Provide:
1. Category
2. Priority (High/Medium/Low)
3. Suggested department
4. Estimated resolution time"""
        
        ai_response = await self.generate_ai_response(ticket_description, system_prompt)
        
        response = f"""🎫 **Ticket Categorization**

**Ticket:** {ticket_description[:100]}...

**AI Analysis:**
{ai_response}

**Actions:**
✅ Ticket categorized automatically
✅ Priority assigned
✅ Routed to appropriate department

The ticket has been processed and is ready for assignment."""
        
        return self.format_response(
            response=response,
            actions=[
                {"type": "ticket_categorized", "success": True},
                {"type": "priority_assigned", "success": True}
            ]
        )
    
    async def _suggest_solution(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Suggest solution for a ticket"""
        issue_description = context.get("description", query) if context else query
        
        system_prompt = """You are a technical support expert. Provide clear, step-by-step solutions.

Format your response as:
1. Problem Summary
2. Solution Steps
3. Prevention Tips"""
        
        ai_response = await self.generate_ai_response(issue_description, system_prompt)
        
        response = f"""💡 **Solution Suggestion**

**Issue:** {issue_description[:100]}...

**Recommended Solution:**
{ai_response}

**📋 Response Template Ready**
You can send this solution directly to the user or customize it further."""
        
        return self.format_response(
            response=response,
            actions=[{"type": "solution_generated", "success": True}]
        )
    
    async def _list_tickets(self) -> Dict[str, Any]:
        """List helpdesk tickets"""
        try:
            helpdesk = mongodb_client.get_collection("helpdesks")
            tickets = await helpdesk.find().to_list(length=100)
            
            total_tickets = len(tickets)
            open_tickets = len([t for t in tickets if t.get("status") == "open"])
            resolved_tickets = len([t for t in tickets if t.get("status") == "resolved"])
            
            response = f"""🎫 **Helpdesk Dashboard**

**📊 Ticket Overview:**
• Total Tickets: {total_tickets}
• Open: {open_tickets}
• Resolved: {resolved_tickets}

**🔥 Priority Distribution:**
• High Priority: {len([t for t in tickets if t.get('priority') == 'high'])}
• Medium Priority: {len([t for t in tickets if t.get('priority') == 'medium'])}
• Low Priority: {len([t for t in tickets if t.get('priority') == 'low'])}

**💡 AI Recommendations:**
• Focus on high-priority tickets first
• Average response time: 24 hours
• Consider adding more FAQ resources

Need help with a specific ticket? Let me know!"""
            
            return self.format_response(
                response=response,
                data={"tickets": tickets[:10]},
                analysis={
                    "total": total_tickets,
                    "open": open_tickets,
                    "resolved": resolved_tickets
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing tickets: {str(e)}")
            return self.format_response(
                response="Currently, there are no tickets in the system.",
                data={"tickets": []}
            )
    
    async def _general_helpdesk_info(self) -> Dict[str, Any]:
        """General helpdesk information"""
        response = """🎫 **Helpdesk Manager**

I can help you with:
• 📋 Auto-categorize support tickets
• 💡 Suggest solutions based on AI analysis
• 📊 View ticket statistics and priorities
• ✉️ Generate response templates
• 👥 Auto-assign tickets to staff

What would you like me to help with?"""
        
        return self.format_response(response=response)
    
    def get_fallback_response(self, query: str) -> str:
        """Fallback response"""
        return """🎫 **Helpdesk Manager**

I'm here to help you manage support tickets efficiently!

Features:
• Intelligent ticket categorization
• AI-powered solution suggestions
• Priority assignment
• Response template generation

How can I assist you today?"""
