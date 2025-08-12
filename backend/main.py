from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import sqlite3
import json
import logging
from datetime import datetime
import uvicorn

from .agents.natural_conversational_agent import NaturalConversationalAgent
from .agents.domain_knowledge import DomainKnowledgeAgent
from .agents.client_profile import ClientProfileAgent
from .agents.actionable_insights import ActionableInsightsAgent
from .agents.meetings import MeetingsAgent
from .database.db_manager import DatabaseManager
from .workflow_orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="K-Square Programme Onboarding Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager("ks_onboarding.db")
orchestrator = WorkflowOrchestrator(db_manager)

# Pydantic models
class DirectSetupRequest(BaseModel):
    client_name: str
    industry: str
    problem_statement: str
    tech_stack: str

class ValidationRequest(BaseModel):
    output_id: int
    relevant: bool
    feedback: Optional[str] = None

class WorkflowExecutionRequest(BaseModel):
    client_data: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    tags: Optional[List[str]] = None

class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ConversationStartRequest(BaseModel):
    session_id: Optional[str] = None

class ConversationResponse(BaseModel):
    response: str
    conversation_id: str
    is_complete: bool
    client_profile: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and load use cases on startup"""
    logger.info("Initializing K-Square Programme Onboarding Agent...")
    db_manager.initialize_database()
    db_manager.load_use_cases()
    logger.info("System initialized successfully")

@app.get("/")
async def root():
    return {"message": "K-Square Programme Onboarding Agent API", "status": "running"}

@app.get("/api/use-cases")
async def get_use_cases():
    """Get available use cases for selection"""
    try:
        use_cases = db_manager.get_use_cases()
        return {"use_cases": use_cases}
    except Exception as e:
        logger.error(f"Error fetching use cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch use cases")

@app.post("/api/conversation/start")
async def start_conversation(request: ConversationStartRequest = None):
    """Start a new conversational setup session"""
    try:
        import uuid
        session_id = request.session_id if request and request.session_id else str(uuid.uuid4())
        result = await orchestrator.natural_conversational_agent.start_conversation(session_id)
        
        return {
            "status": "started",
            "conversation_id": session_id,
            "session_id": session_id,
            "message": result.get("message"),
            "client_info": result.get("client_info", {}),
            "completion_percentage": result.get("completion_percentage", 0),
            "is_complete": result.get("is_complete", False)
        }
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@app.post("/api/conversation/message")
async def send_message(request: ConversationRequest):
    """Send a message in the conversational setup"""
    try:
        if not request.conversation_id:
            raise HTTPException(status_code=400, detail="Conversation ID is required")
        
        result = await orchestrator.natural_conversational_agent.process_message(
            request.conversation_id, 
            request.message
        )
        
        return {
            "status": "success",
            "conversation_id": request.conversation_id,
            "response": result.get("response"),
            "message": result.get("response"),
            "client_info": result.get("client_info", {}),
            "completion_percentage": result.get("completion_percentage", 0),
            "missing_fields": result.get("missing_fields", []),
            "is_complete": result.get("is_complete", False)
        }
    except Exception as e:
        logger.error(f"Error processing conversation message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/api/conversation/{conversation_id}/status")
async def get_conversation_status(conversation_id: str):
    """Get the current status of a conversation"""
    try:
        status = orchestrator.natural_conversational_agent.get_session_status(conversation_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return {
            "conversation_id": conversation_id,
            "client_info": status.get("client_info", {}),
            "completion_percentage": status.get("completion_percentage", 0),
            "missing_fields": status.get("missing_fields", []),
            "is_complete": status.get("is_complete", False),
            "message_count": status.get("message_count", 0)
        }
    except Exception as e:
        logger.error(f"Error getting conversation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation status: {str(e)}")

@app.post("/api/validate")
async def validate_output(request: ValidationRequest):
    """Accept user validation for agent outputs"""
    try:
        db_manager.store_validation(
            output_id=request.output_id,
            relevant=request.relevant,
            feedback=request.feedback
        )
        
        logger.info(f"Validation stored for output {request.output_id}: {request.relevant}")
        return {"status": "success", "message": "Validation stored successfully"}
    except Exception as e:
        logger.error(f"Error storing validation: {e}")
        raise HTTPException(status_code=500, detail="Failed to store validation")

@app.post("/api/execute-workflow")
async def execute_workflow(request: WorkflowExecutionRequest):
    """Execute the full workflow for client onboarding"""
    try:
        logger.info(f"Executing full workflow for client: {request.client_data.get('client_name', 'Unknown')}")
        
        start_time = datetime.now()
        result = await orchestrator.execute_full_workflow(request.client_data)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Workflow completed in {execution_time:.2f} seconds")
        
        return {
            "status": "success",
            "message": "Workflow executed successfully",
            "result": result,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Retrieve tagged data from Knowledge Base for dashboard display"""
    try:
        # Get data from database
        client_profiles = db_manager.get_client_profiles()
        domain_knowledge = db_manager.get_domain_knowledge()
        meeting_insights = db_manager.get_meeting_insights()
        recommendations = db_manager.get_recommendations()
        
        # Get actual client profiles from the profiles table
        conn = sqlite3.connect('ks_onboarding.db')
        cursor = conn.cursor()
        
        # Get all profiles
        cursor.execute("SELECT profile_data FROM profiles ORDER BY created_at DESC")
        profile_results = cursor.fetchall()
        
        actual_profiles = []
        for result in profile_results:
            if result[0]:
                profile_data = json.loads(result[0])
                actual_profiles.append(profile_data)
        
        # Get insights count
        cursor.execute("SELECT COUNT(*) FROM insights")
        insights_count = cursor.fetchone()[0]
        
        # Get meetings data (using our mock data)
        meetings_data = [
            {
                "id": "1",
                "title": "Initial Discovery Call",
                "date": "2024-01-14",
                "duration": 60,
                "participants": ["Client CEO", "K-Square Consultant"],
                "sentiment_score": 0.78,
                "engagement_score": 0.85
            },
            {
                "id": "2", 
                "title": "Technical Requirements Review",
                "date": "2024-01-16",
                "duration": 45,
                "participants": ["Client CTO", "K-Square Technical Lead"],
                "sentiment_score": 0.82,
                "engagement_score": 0.90
            }
        ]
        
        conn.close()
        
        # Structure data for frontend
        dashboard_data = {
            "client_profiles": actual_profiles,
            "domain_knowledge": domain_knowledge,
            "meeting_insights": meeting_insights,
            "recommendations": recommendations,
            "insights": [{"id": i, "type": "insight"} for i in range(insights_count)],
            "meetings": meetings_data,
            "system_metrics": {
                "total_workflows": len(actual_profiles),
                "active_workflows": len(actual_profiles),
                "completed_workflows": len(actual_profiles),
                "failed_workflows": 0
            }
        }
        
        return {
            "status": "success",
            "data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@app.post("/api/search")
async def search_knowledge_base(request: SearchRequest):
    """Query Knowledge Base for specific tags or keywords"""
    try:
        results = db_manager.search_knowledge_base(
            query=request.query,
            tags=request.tags
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge base")

@app.get("/api/clients")
async def get_client_profiles():
    """Get all client profiles"""
    try:
        conn = sqlite3.connect('ks_onboarding.db')
        cursor = conn.cursor()
        
        # Get all profiles from the profiles table
        cursor.execute("SELECT profile_data FROM profiles ORDER BY created_at DESC")
        results = cursor.fetchall()
        
        profiles = []
        for result in results:
            if result[0]:
                profile_data = json.loads(result[0])
                profiles.append(profile_data)
        
        # If no profiles exist, check for setup data as fallback
        if not profiles:
            cursor.execute("SELECT setup_data FROM setup_sessions ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result and result[0]:
                setup_data = json.loads(result[0])
                client_profile = {
                    "id": "1",
                    "company_name": setup_data.get("client_name", "Unknown"),
                    "industry": setup_data.get("industry", "Unknown"),
                    "company_size": "150 employees",
                    "founding_year": 2010,
                    "regions": ["North America"],
                    "stakeholders": ["CEO", "CTO", "Operations Manager"],
                    "completeness_score": 85,
                    "insights": {
                        "market_position": "Mid-market leader",
                        "growth_potential": "High",
                        "risk_factors": ["Technology debt", "Market competition"],
                        "recommendations": ["Modernize tech stack", "Improve data integration"]
                    },
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                profiles.append(client_profile)
        
        conn.close()
        return {"status": "success", "data": profiles}
        
    except Exception as e:
        logger.error(f"Error getting client profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clients/{client_name}")
async def get_client_profile(client_name: str):
    """Get specific client profile"""
    try:
        conn = sqlite3.connect('ks_onboarding.db')
        cursor = conn.cursor()
        
        # First, try to find the profile in the profiles table
        cursor.execute("SELECT profile_data FROM profiles WHERE client_name = ?", (client_name,))
        result = cursor.fetchone()
        
        if result and result[0]:
            profile_data = json.loads(result[0])
            conn.close()
            return {"status": "success", "data": profile_data}
        
        # If not found in profiles, check setup_sessions as fallback
        cursor.execute("SELECT setup_data FROM setup_sessions ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result and result[0]:
            setup_data = json.loads(result[0])
            if setup_data.get("client_name", "").lower() == client_name.lower():
                client_profile = {
                    "id": "1",
                    "company_name": setup_data.get("client_name", "Unknown"),
                    "industry": setup_data.get("industry", "Unknown"),
                    "problem_statement": setup_data.get("problem_statement", ""),
                    "tech_stack": setup_data.get("tech_stack", ""),
                    "timeline": setup_data.get("timeline", ""),
                    "company_size": "150 employees",
                    "founding_year": 2010,
                    "regions": ["North America"],
                    "stakeholders": ["CEO", "CTO", "Operations Manager"],
                    "completeness_score": 85,
                    "insights": {
                        "market_position": "Mid-market leader",
                        "growth_potential": "High",
                        "risk_factors": ["Technology debt", "Market competition"],
                        "recommendations": ["Modernize tech stack", "Improve data integration"]
                    },
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                conn.close()
                return {"status": "success", "data": client_profile}
        
        conn.close()
        raise HTTPException(status_code=404, detail="Client not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clients")
async def create_client_profile(profile_data: Dict[str, Any]):
    """Create a new client profile"""
    try:
        conn = sqlite3.connect('ks_onboarding.db')
        cursor = conn.cursor()
        
        # Create a new profile with generated ID
        profile_id = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare profile data with defaults
        client_profile = {
            "id": profile_id,
            "company_name": profile_data.get("company_name", ""),
            "industry": profile_data.get("industry", ""),
            "company_size": profile_data.get("company_size", "Unknown"),
            "founding_year": profile_data.get("founding_year", datetime.now().year),
            "regions": profile_data.get("regions", []),
            "stakeholders": profile_data.get("stakeholders", []),
            "completeness_score": 75,
            "insights": {
                "market_position": "To be determined",
                "growth_potential": "Medium",
                "risk_factors": ["Market competition"],
                "recommendations": ["Complete profile setup"]
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store in profiles table
        cursor.execute(
            "INSERT INTO profiles (client_name, profile_data, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (client_profile["company_name"], json.dumps(client_profile), datetime.now().isoformat(), datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created new client profile: {client_profile['company_name']}")
        return {"status": "success", "data": client_profile, "message": "Profile created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating client profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/clients/{profile_id}")
async def update_client_profile(profile_id: str, profile_data: Dict[str, Any]):
    """Update an existing client profile"""
    try:
        conn = sqlite3.connect('ks_onboarding.db')
        cursor = conn.cursor()
        
        # Get existing profile
        cursor.execute("SELECT profile_data FROM profiles WHERE client_name = ?", (profile_data.get("company_name", ""),))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update profile data
        existing_profile = json.loads(result[0])
        existing_profile.update(profile_data)
        existing_profile["updated_at"] = datetime.now().isoformat()
        
        # Update in database
        cursor.execute(
            "UPDATE profiles SET profile_data = ?, updated_at = ? WHERE client_name = ?",
            (json.dumps(existing_profile), datetime.now().isoformat(), profile_data.get("company_name", ""))
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated client profile: {profile_data.get('company_name', '')}")
        return {"status": "success", "data": existing_profile, "message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/clients/{profile_id}")
async def delete_client_profile(profile_id: str):
    """Delete a client profile"""
    try:
        conn = sqlite3.connect('ks_onboarding.db')
        cursor = conn.cursor()
        
        # Delete profile
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Profile not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted client profile: {profile_id}")
        return {"status": "success", "message": "Profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights(client_name: Optional[str] = None):
    """Get insights data"""
    try:
        # Return mock insights data
        insights = [
            {
                "id": "1",
                "title": "Technology Integration Opportunity",
                "description": "Consolidating multiple systems could improve efficiency by 30%",
                "priority": "high",
                "type": "strategic",
                "impact_score": 8.5,
                "effort_estimate": "3-6 months",
                "timeline": "Q2 2024",
                "resources_required": ["Development Team", "System Architect"],
                "success_metrics": ["30% efficiency improvement", "Reduced system maintenance"],
                "risk_factors": ["Integration complexity", "Data migration risks"],
                "recommendations": ["Start with pilot integration", "Conduct thorough testing"],
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "2",
                "title": "Customer Data Unification",
                "description": "Unified customer view could increase retention by 15%",
                "priority": "medium",
                "type": "tactical",
                "impact_score": 7.2,
                "effort_estimate": "2-4 months",
                "timeline": "Q3 2024",
                "resources_required": ["Data Team", "Analytics Specialist"],
                "success_metrics": ["15% retention increase", "Improved customer satisfaction"],
                "risk_factors": ["Data quality issues", "Privacy compliance"],
                "recommendations": ["Implement data governance", "Start with key customer segments"],
                "status": "in_progress",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        return {"status": "success", "data": insights}
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/summary")
async def get_insights_summary():
    """Get insights summary data"""
    try:
        summary = {
            "total_insights": 2,
            "high_priority": 1,
            "medium_priority": 1,
            "low_priority": 0,
            "completed": 0,
            "in_progress": 1,
            "pending": 1,
            "average_impact": 7.85,
            "project_health_score": 8.2
        }
        return {"status": "success", "data": summary}
    except Exception as e:
        logger.error(f"Error getting insights summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/insights/generate")
async def generate_insights():
    """Generate new insights"""
    try:
        # Mock insight generation
        new_insight = {
            "id": "3",
            "title": "Process Automation Opportunity",
            "description": "Automating manual processes could save 20 hours per week",
            "priority": "high",
            "type": "opportunity",
            "impact_score": 8.0,
            "effort_estimate": "1-2 months",
            "timeline": "Q1 2024",
            "resources_required": ["Automation Specialist", "Process Analyst"],
            "success_metrics": ["20 hours saved per week", "Reduced manual errors"],
            "risk_factors": ["Change management", "Training requirements"],
            "recommendations": ["Identify high-impact processes first", "Pilot with one department"],
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return {"status": "success", "data": new_insight, "message": "New insight generated successfully"}
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/insights/{insight_id}")
async def update_insight_status(insight_id: str, status_data: dict):
    """Update insight status"""
    try:
        status = status_data.get("status")
        logger.info(f"Updated insight {insight_id} status to {status}")
        return {"status": "success", "message": f"Insight status updated to {status}"}
    except Exception as e:
        logger.error(f"Error updating insight status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/export")
async def export_insights(format: str = "csv"):
    """Export insights in specified format"""
    # Mock export functionality
    return {"message": f"Insights exported in {format} format", "download_url": "/downloads/insights.csv"}

@app.get("/api/meetings")
async def get_meetings(client_name: Optional[str] = None):
    """Get meetings data"""
    try:
        # Return mock meetings data with realistic content
        meetings = [
            {
                "id": "1",
                "title": "Initial Discovery Call",
                "date": "2024-01-15",
                "duration": 3600,  # 60 minutes in seconds
                "participants": ["Sarah Johnson (CEO)", "Mike Chen (K-Square Consultant)"],
                "transcript": "Mike: Good morning Sarah, thank you for taking the time to meet with us today. I'd love to start by understanding your current business challenges.\n\nSarah: Good morning Mike. We're facing significant issues with our supply chain visibility. Our current systems are fragmented, and we're struggling to track inventory across multiple warehouses.\n\nMike: That's a common challenge we see in manufacturing. Can you tell me more about the impact this is having on your operations?\n\nSarah: Absolutely. We're experiencing stockouts in some locations while having excess inventory in others. It's affecting our customer satisfaction and tying up working capital.\n\nMike: I understand. What systems are you currently using for inventory management?\n\nSarah: We have an older ERP system that's about 10 years old, plus some Excel spreadsheets for tracking. It's not integrated well.\n\nMike: That makes sense. Have you considered modernizing your tech stack? We've helped similar companies implement real-time inventory tracking solutions.\n\nSarah: Yes, that's exactly what we're looking for. We need better visibility and automation. What would be your recommended approach?\n\nMike: I'd suggest starting with a comprehensive assessment of your current processes, then implementing a phased approach to modernization. We can discuss specific technologies that would work best for your use case.",
                "sentiment_score": 0.78,
                "engagement_score": 0.85,
                "action_items": [
                    "Schedule follow-up technical assessment meeting",
                    "Prepare current system architecture documentation",
                    "Review budget allocation for modernization project",
                    "Identify key stakeholders for project team"
                ],
                "key_topics": [
                    "Supply Chain Visibility",
                    "Inventory Management",
                    "ERP Modernization",
                    "System Integration",
                    "Real-time Tracking"
                ],
                "summary": "Initial discovery call with Sarah Johnson (CEO) to discuss supply chain visibility challenges. Client is experiencing inventory management issues due to fragmented systems and outdated ERP. Key pain points include stockouts, excess inventory, and poor system integration. Recommended phased modernization approach with comprehensive assessment as first step.",
                "insights": {
                    "positive_sentiment": 0.65,
                    "negative_sentiment": 0.15,
                    "neutral_sentiment": 0.20,
                    "key_decisions": [
                        "Proceed with comprehensive system assessment",
                        "Adopt phased modernization approach",
                        "Focus on real-time inventory tracking as priority"
                    ],
                    "concerns_raised": [
                        "Budget constraints for full system overhaul",
                        "Potential disruption during transition period",
                        "Integration complexity with existing systems"
                    ],
                    "next_steps": [
                        "Schedule technical assessment meeting",
                        "Prepare detailed project proposal",
                        "Identify pilot implementation scope"
                    ]
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "2",
                "title": "Technical Requirements Review",
                "date": "2024-01-22",
                "duration": 2700,  # 45 minutes in seconds
                "participants": ["Sarah Johnson (CEO)", "Tom Wilson (CTO)", "Mike Chen (K-Square Consultant)"],
                "transcript": "Mike: Thank you both for joining today's technical review. Tom, I'd like to understand your current architecture better.\n\nTom: Sure, we're running on a legacy Oracle ERP system with some custom modules. We also have separate systems for warehouse management and customer orders.\n\nMike: How do these systems communicate with each other currently?\n\nTom: Mostly through batch processes that run overnight. We have some real-time integrations, but they're fragile and often break.\n\nSarah: That's exactly the problem. We don't get real-time visibility into our operations.\n\nMike: I see. What's your current cloud strategy? Are you open to cloud-based solutions?\n\nTom: We're definitely interested in cloud. We've been moving some applications to AWS, but our core ERP is still on-premises.\n\nMike: That's a good foundation. We could design a hybrid approach that leverages your existing AWS infrastructure while modernizing your inventory management.\n\nSarah: What kind of timeline are we looking at for implementation?\n\nMike: For a phased approach, we could have the first phase operational in 3-4 months, with full implementation over 12-18 months.",
                "sentiment_score": 0.82,
                "engagement_score": 0.90,
                "action_items": [
                    "Provide detailed technical architecture proposal",
                    "Schedule AWS infrastructure review",
                    "Prepare integration roadmap document",
                    "Define Phase 1 scope and deliverables"
                ],
                "key_topics": [
                    "Legacy ERP Systems",
                    "Cloud Migration Strategy",
                    "System Integration",
                    "AWS Infrastructure",
                    "Implementation Timeline"
                ],
                "summary": "Technical requirements review with CEO and CTO. Discussed current Oracle ERP system, integration challenges, and cloud migration strategy. Team is aligned on hybrid cloud approach leveraging existing AWS infrastructure. Defined phased implementation timeline of 12-18 months with first phase in 3-4 months.",
                "insights": {
                    "positive_sentiment": 0.70,
                    "negative_sentiment": 0.10,
                    "neutral_sentiment": 0.20,
                    "key_decisions": [
                        "Adopt hybrid cloud architecture approach",
                        "Leverage existing AWS infrastructure",
                        "Implement in phases over 12-18 months"
                    ],
                    "concerns_raised": [
                        "Integration complexity with legacy systems",
                        "Potential downtime during migration",
                        "Resource allocation for parallel systems"
                    ],
                    "next_steps": [
                        "Develop detailed technical proposal",
                        "Conduct AWS infrastructure assessment",
                        "Create project timeline and milestones"
                    ]
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        return {"status": "success", "data": meetings}
    except Exception as e:
        logger.error(f"Error getting meetings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/summary")
async def get_meetings_summary():
    """Get meetings summary statistics"""
    return {
        "total_meetings": 2,
        "total_duration": 105.0,  # Total minutes from both meetings
        "average_sentiment": 0.80,  # Average of 0.78 and 0.82
        "average_engagement": 0.875,  # Average of 0.85 and 0.90
        "completed_action_items": 6,
        "total_action_items": 8
    }

@app.post("/api/meetings/upload")
async def upload_meeting(meeting_data: dict):
    """Upload a new meeting"""
    # Mock upload functionality
    return {
        "id": "meeting_" + str(len(meeting_data)),
        "message": "Meeting uploaded successfully",
        "status": "processing"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "connected" if db_manager.check_connection() else "disconnected"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)