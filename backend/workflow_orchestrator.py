import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import all agents
from .agents.programme_setup import ProgrammeSetupAgent
from .agents.domain_knowledge import DomainKnowledgeAgent
from .agents.client_profile import ClientProfileAgent
from .agents.actionable_insights import ActionableInsightsAgent
from .agents.meetings import MeetingsAgent

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Orchestrates the workflow between all agents in the K-Square Programme Onboarding system"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Initialize all agents
        self.programme_setup_agent = ProgrammeSetupAgent(db_manager)
        self.domain_knowledge_agent = DomainKnowledgeAgent(db_manager)
        self.client_profile_agent = ClientProfileAgent(db_manager)
        self.actionable_insights_agent = ActionableInsightsAgent(db_manager)
        self.meetings_agent = MeetingsAgent(db_manager)
        
        self.workflow_state = {}
        
        logger.info("WorkflowOrchestrator initialized with all agents")
    
    async def execute_full_workflow(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete workflow for a new client onboarding"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting full workflow {workflow_id} for client: {client_data.get('client_name', 'Unknown')}")
        
        try:
            # Initialize workflow state
            self.workflow_state[workflow_id] = {
                "status": "running",
                "start_time": start_time.isoformat(),
                "client_data": client_data,
                "agent_results": {},
                "current_step": "programme_setup"
            }
            
            # Step 1: Programme Setup
            logger.info(f"Workflow {workflow_id}: Starting Programme Setup")
            setup_result = await self.programme_setup_agent.process_setup(client_data)
            self.workflow_state[workflow_id]["agent_results"]["programme_setup"] = setup_result
            self.workflow_state[workflow_id]["current_step"] = "domain_knowledge"
            
            if setup_result.get("status") != "success":
                raise Exception(f"Programme Setup failed: {setup_result.get('message')}")
            
            # Step 2: Domain Knowledge Analysis
            logger.info(f"Workflow {workflow_id}: Starting Domain Knowledge Analysis")
            domain_result = await self.domain_knowledge_agent.analyze_domain(
                client_data.get("industry", ""),
                client_data.get("problem_statement", ""),
                client_data.get("tech_stack", [])
            )
            self.workflow_state[workflow_id]["agent_results"]["domain_knowledge"] = domain_result
            self.workflow_state[workflow_id]["current_step"] = "client_profile"
            
            if domain_result.get("status") != "success":
                raise Exception(f"Domain Knowledge Analysis failed: {domain_result.get('message')}")
            
            # Step 3: Client Profile Building
            logger.info(f"Workflow {workflow_id}: Starting Client Profile Building")
            profile_result = await self.client_profile_agent.build_profile(client_data)
            self.workflow_state[workflow_id]["agent_results"]["client_profile"] = profile_result
            self.workflow_state[workflow_id]["current_step"] = "meetings_analysis"
            
            if profile_result.get("status") != "success":
                raise Exception(f"Client Profile Building failed: {profile_result.get('message')}")
            
            # Step 4: Meetings Analysis (if meeting data available)
            logger.info(f"Workflow {workflow_id}: Starting Meetings Analysis")
            meeting_result = await self._analyze_meetings_for_client(client_data.get("client_name", ""))
            self.workflow_state[workflow_id]["agent_results"]["meetings"] = meeting_result
            self.workflow_state[workflow_id]["current_step"] = "actionable_insights"
            
            # Step 5: Generate Actionable Insights
            logger.info(f"Workflow {workflow_id}: Generating Actionable Insights")
            insights_result = await self.actionable_insights_agent.generate_insights(
                client_data.get("client_name", ""),
                domain_result,
                profile_result,
                meeting_result
            )
            self.workflow_state[workflow_id]["agent_results"]["actionable_insights"] = insights_result
            self.workflow_state[workflow_id]["current_step"] = "completed"
            
            if insights_result.get("status") != "success":
                raise Exception(f"Actionable Insights generation failed: {insights_result.get('message')}")
            
            # Finalize workflow
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.workflow_state[workflow_id].update({
                "status": "completed",
                "end_time": end_time.isoformat(),
                "execution_time": execution_time
            })
            
            # Generate final summary
            final_result = self._generate_workflow_summary(workflow_id)
            
            logger.info(f"Workflow {workflow_id} completed successfully in {execution_time:.2f} seconds")
            return final_result
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            self.workflow_state[workflow_id].update({
                "status": "failed",
                "error": str(e),
                "end_time": datetime.now().isoformat()
            })
            
            return {
                "status": "error",
                "workflow_id": workflow_id,
                "message": f"Workflow execution failed: {str(e)}",
                "partial_results": self.workflow_state[workflow_id].get("agent_results", {})
            }
    
    async def execute_single_agent(self, agent_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a single agent independently"""
        logger.info(f"Executing single agent: {agent_name}")
        
        try:
            if agent_name == "programme_setup":
                return await self.programme_setup_agent.process_setup(kwargs.get("client_data", {}))
            
            elif agent_name == "domain_knowledge":
                return await self.domain_knowledge_agent.analyze_domain(
                    kwargs.get("industry", ""),
                    kwargs.get("problem_statement", ""),
                    kwargs.get("tech_stack", [])
                )
            
            elif agent_name == "client_profile":
                return await self.client_profile_agent.build_profile(kwargs.get("client_data", {}))
            
            elif agent_name == "meetings":
                return await self.meetings_agent.analyze_meeting(
                    kwargs.get("meeting_id", ""),
                    kwargs.get("transcript", "")
                )
            
            elif agent_name == "actionable_insights":
                return await self.actionable_insights_agent.generate_insights(
                    kwargs.get("client_name", ""),
                    kwargs.get("domain_knowledge", {}),
                    kwargs.get("client_profile", {}),
                    kwargs.get("meeting_analysis", {})
                )
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown agent: {agent_name}"
                }
                
        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {e}")
            return {
                "status": "error",
                "message": f"Agent execution failed: {str(e)}"
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow"""
        if workflow_id not in self.workflow_state:
            return {
                "status": "error",
                "message": "Workflow not found"
            }
        
        return {
            "status": "success",
            "workflow_state": self.workflow_state[workflow_id]
        }
    
    async def get_dashboard_data(self, client_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get basic dashboard data from database
            dashboard_data = self.db_manager.get_dashboard_data()
            
            # Enhance with workflow insights if client specified
            if client_name:
                # Find the most recent workflow for this client
                client_workflows = [
                    (wf_id, wf_data) for wf_id, wf_data in self.workflow_state.items()
                    if wf_data.get("client_data", {}).get("client_name") == client_name
                ]
                
                if client_workflows:
                    # Get the most recent workflow
                    latest_workflow = max(client_workflows, key=lambda x: x[1].get("start_time", ""))
                    workflow_id, workflow_data = latest_workflow
                    
                    # Add workflow-specific insights
                    dashboard_data["client_specific"] = {
                        "workflow_id": workflow_id,
                        "workflow_status": workflow_data.get("status"),
                        "current_step": workflow_data.get("current_step"),
                        "agent_results": workflow_data.get("agent_results", {})
                    }
            
            # Add system-wide metrics
            dashboard_data["system_metrics"] = {
                "total_workflows": len(self.workflow_state),
                "active_workflows": len([wf for wf in self.workflow_state.values() if wf.get("status") == "running"]),
                "completed_workflows": len([wf for wf in self.workflow_state.values() if wf.get("status") == "completed"]),
                "failed_workflows": len([wf for wf in self.workflow_state.values() if wf.get("status") == "failed"])
            }
            
            return {
                "status": "success",
                "dashboard_data": dashboard_data
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                "status": "error",
                "message": f"Failed to get dashboard data: {str(e)}"
            }
    
    async def validate_programme_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate programme data using the Programme Setup Agent"""
        try:
            return await self.programme_setup_agent.validate_input(client_data)
        except Exception as e:
            logger.error(f"Error validating programme data: {e}")
            return {
                "status": "error",
                "message": f"Validation failed: {str(e)}"
            }
    
    async def search_knowledge_base(self, query: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """Search the knowledge base"""
        try:
            # Use domain knowledge agent for enhanced search
            if industry:
                domain_result = await self.domain_knowledge_agent.analyze_domain(industry, query, [])
                knowledge_data = domain_result.get("domain_knowledge", {})
            else:
                knowledge_data = {}
            
            # Get database search results
            db_results = self.db_manager.search_knowledge_base(query)
            
            return {
                "status": "success",
                "search_results": {
                    "database_results": db_results,
                    "domain_insights": knowledge_data,
                    "query": query,
                    "industry_filter": industry
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return {
                "status": "error",
                "message": f"Knowledge base search failed: {str(e)}"
            }
    
    async def _analyze_meetings_for_client(self, client_name: str) -> Dict[str, Any]:
        """Analyze all meetings for a specific client"""
        try:
            # Get meetings from database
            meetings = self.db_manager.get_meetings_by_client(client_name)
            
            if not meetings:
                return {
                    "status": "success",
                    "message": "No meetings found for client",
                    "meeting_analysis": {
                        "total_meetings": 0,
                        "sentiment": {"category": "neutral", "polarity": 0, "subjectivity": 0},
                        "action_items": [],
                        "engagement_metrics": {"average_engagement": 0},
                        "key_topics": [],
                        "participants": []
                    }
                }
            
            # Analyze the most recent meeting
            latest_meeting = meetings[0]  # Assuming meetings are ordered by date
            
            result = await self.meetings_agent.analyze_meeting(
                latest_meeting.get("id", ""),
                latest_meeting.get("transcript", "")
            )
            
            # Add summary of all meetings
            if result.get("status") == "success":
                result["meeting_analysis"]["total_meetings"] = len(meetings)
                result["meeting_analysis"]["meeting_history"] = [
                    {
                        "id": meeting.get("id"),
                        "date": meeting.get("date"),
                        "duration": meeting.get("duration"),
                        "participants": meeting.get("participants", [])
                    }
                    for meeting in meetings
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing meetings for client {client_name}: {e}")
            return {
                "status": "error",
                "message": f"Meeting analysis failed: {str(e)}"
            }
    
    def _generate_workflow_summary(self, workflow_id: str) -> Dict[str, Any]:
        """Generate a comprehensive summary of the workflow execution"""
        workflow_data = self.workflow_state[workflow_id]
        agent_results = workflow_data.get("agent_results", {})
        
        # Extract key insights from each agent
        summary = {
            "workflow_id": workflow_id,
            "status": workflow_data.get("status"),
            "execution_time": workflow_data.get("execution_time"),
            "client_name": workflow_data.get("client_data", {}).get("client_name"),
            "summary": {
                "programme_setup": self._extract_setup_summary(agent_results.get("programme_setup", {})),
                "domain_knowledge": self._extract_domain_summary(agent_results.get("domain_knowledge", {})),
                "client_profile": self._extract_profile_summary(agent_results.get("client_profile", {})),
                "meetings": self._extract_meetings_summary(agent_results.get("meetings", {})),
                "actionable_insights": self._extract_insights_summary(agent_results.get("actionable_insights", {}))
            },
            "full_results": agent_results
        }
        
        return summary
    
    def _extract_setup_summary(self, setup_result: Dict) -> Dict[str, Any]:
        """Extract summary from programme setup results"""
        return {
            "validation_status": setup_result.get("validation", {}).get("is_valid", False),
            "completeness_score": setup_result.get("validation", {}).get("completeness_score", 0),
            "missing_fields": setup_result.get("validation", {}).get("missing_fields", []),
            "conversation_prompt": setup_result.get("conversation_prompt", "")
        }
    
    def _extract_domain_summary(self, domain_result: Dict) -> Dict[str, Any]:
        """Extract summary from domain knowledge results"""
        domain_knowledge = domain_result.get("domain_knowledge", {})
        return {
            "industry": domain_knowledge.get("industry", ""),
            "confidence_score": domain_result.get("confidence_score", 0),
            "best_practices_count": len(domain_knowledge.get("best_practices", [])),
            "tech_compatibility": domain_knowledge.get("tech_analysis", {}).get("compatibility_score", 0),
            "recommendations_count": len(domain_knowledge.get("recommendations", []))
        }
    
    def _extract_profile_summary(self, profile_result: Dict) -> Dict[str, Any]:
        """Extract summary from client profile results"""
        return {
            "completeness_score": profile_result.get("completeness_score", 0),
            "company_size": profile_result.get("client_profile", {}).get("company_size", ""),
            "industry": profile_result.get("client_profile", {}).get("industry", ""),
            "complexity_level": profile_result.get("client_profile", {}).get("current_project", {}).get("complexity_level", ""),
            "insights_count": len(profile_result.get("insights", []))
        }
    
    def _extract_meetings_summary(self, meetings_result: Dict) -> Dict[str, Any]:
        """Extract summary from meetings analysis results"""
        meeting_analysis = meetings_result.get("meeting_analysis", {})
        return {
            "total_meetings": meeting_analysis.get("total_meetings", 0),
            "sentiment_category": meeting_analysis.get("sentiment", {}).get("category", "neutral"),
            "action_items_count": len(meeting_analysis.get("action_items", [])),
            "engagement_score": meeting_analysis.get("engagement_metrics", {}).get("average_engagement", 0),
            "key_topics_count": len(meeting_analysis.get("key_topics", []))
        }
    
    def _extract_insights_summary(self, insights_result: Dict) -> Dict[str, Any]:
        """Extract summary from actionable insights results"""
        insights = insights_result.get("insights", {})
        return {
            "project_health_score": insights.get("project_health_score", {}).get("overall_score", 0),
            "health_level": insights.get("project_health_score", {}).get("health_level", "unknown"),
            "strategic_recommendations_count": len(insights.get("strategic_recommendations", [])),
            "tactical_actions_count": len(insights.get("tactical_actions", [])),
            "risks_identified": len(insights.get("risk_assessment", {}).get("risks", [])),
            "risk_level": insights.get("risk_assessment", {}).get("risk_level", "unknown")
        }
    
    def get_all_workflows(self) -> Dict[str, Any]:
        """Get information about all workflows"""
        return {
            "total_workflows": len(self.workflow_state),
            "workflows": {
                workflow_id: {
                    "status": workflow_data.get("status"),
                    "client_name": workflow_data.get("client_data", {}).get("client_name"),
                    "start_time": workflow_data.get("start_time"),
                    "current_step": workflow_data.get("current_step"),
                    "execution_time": workflow_data.get("execution_time")
                }
                for workflow_id, workflow_data in self.workflow_state.items()
            }
        }