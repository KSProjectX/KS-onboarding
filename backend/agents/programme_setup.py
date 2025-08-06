import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ProgrammeSetupAgent:
    """Programme Setup Agent for conversational AI data input and validation"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.name = "Programme Setup Agent"
    
    async def process_setup(self, client_name: str, industry: str, 
                          problem_statement: str, tech_stack: str) -> Dict[str, Any]:
        """Process programme setup with validation"""
        start_time = datetime.now()
        
        try:
            # Validate input data
            validation_result = self._validate_input(
                client_name, industry, problem_statement, tech_stack
            )
            
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["message"],
                    "agent": self.name
                }
            
            # Check if this is a predefined use case
            use_cases = self.db_manager.get_use_cases()
            matching_case = None
            
            for case in use_cases:
                if case["client_name"].lower() == client_name.lower():
                    matching_case = case
                    break
            
            if matching_case:
                logger.info(f"Found matching use case for {client_name}")
                result = {
                    "status": "success",
                    "message": f"Programme setup completed for {client_name}",
                    "data": {
                        "client_name": client_name,
                        "industry": industry,
                        "problem_statement": problem_statement,
                        "tech_stack": tech_stack,
                        "use_case_match": True,
                        "use_case_id": matching_case["id"]
                    },
                    "agent": self.name,
                    "validation": validation_result
                }
            else:
                # Handle new case (not in predefined use cases)
                logger.info(f"Processing new case for {client_name}")
                result = {
                    "status": "success",
                    "message": f"Programme setup completed for new client {client_name}",
                    "data": {
                        "client_name": client_name,
                        "industry": industry,
                        "problem_statement": problem_statement,
                        "tech_stack": tech_stack,
                        "use_case_match": False,
                        "use_case_id": None
                    },
                    "agent": self.name,
                    "validation": validation_result
                }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            logger.info(f"{self.name} completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return {
                "status": "error",
                "message": f"Programme setup failed: {str(e)}",
                "agent": self.name
            }
    
    def _validate_input(self, client_name: str, industry: str, 
                       problem_statement: str, tech_stack: str) -> Dict[str, Any]:
        """Validate input data sufficiency"""
        errors = []
        
        if not client_name or len(client_name.strip()) < 2:
            errors.append("Client name must be at least 2 characters long")
        
        if not industry or len(industry.strip()) < 2:
            errors.append("Industry must be specified")
        
        if not problem_statement or len(problem_statement.strip()) < 10:
            errors.append("Problem statement must be at least 10 characters long")
        
        if not tech_stack or len(tech_stack.strip()) < 2:
            errors.append("Technology stack must be specified")
        
        if errors:
            return {
                "valid": False,
                "message": "Input validation failed: " + "; ".join(errors),
                "errors": errors
            }
        
        return {
            "valid": True,
            "message": "Input validation successful",
            "completeness_score": self._calculate_completeness_score(
                client_name, industry, problem_statement, tech_stack
            )
        }
    
    def _calculate_completeness_score(self, client_name: str, industry: str,
                                    problem_statement: str, tech_stack: str) -> float:
        """Calculate data completeness score (0-1)"""
        scores = []
        
        # Client name score
        scores.append(min(len(client_name.strip()) / 20, 1.0))
        
        # Industry score
        scores.append(min(len(industry.strip()) / 15, 1.0))
        
        # Problem statement score
        scores.append(min(len(problem_statement.strip()) / 100, 1.0))
        
        # Tech stack score
        tech_items = len([item.strip() for item in tech_stack.split(',') if item.strip()])
        scores.append(min(tech_items / 3, 1.0))
        
        return round(sum(scores) / len(scores), 2)
    
    def get_conversation_prompts(self) -> Dict[str, str]:
        """Get conversation prompts for the chat interface"""
        return {
            "welcome": "Welcome to the K-Square Programme Onboarding Agent! I'll help you set up your programme. Please select a client or provide new client details.",
            "select_client": "Choose from existing clients: GT Automotive, MediCare Solutions, ShopTrend Inc., or provide new client information.",
            "client_name": "What is the client name?",
            "industry": "What industry does the client operate in?",
            "problem_statement": "Please describe the problem statement or project requirements.",
            "tech_stack": "What technologies or tech stack will be used?",
            "confirmation": "Please confirm if this information is complete and accurate.",
            "success": "Great! I have all the information needed. Processing your programme setup..."
        }
    
    def generate_setup_summary(self, data: Dict[str, Any]) -> str:
        """Generate a summary of the setup process"""
        return f"""
        Programme Setup Summary:
        
        Client: {data['client_name']}
        Industry: {data['industry']}
        Problem Statement: {data['problem_statement']}
        Technology Stack: {data['tech_stack']}
        
        Setup Status: Completed Successfully
        Data Completeness: {data.get('validation', {}).get('completeness_score', 'N/A')}
        Use Case Match: {'Yes' if data.get('use_case_match') else 'No'}
        
        Next Steps:
        1. Domain Knowledge Agent will analyze industry best practices
        2. Client Profile Agent will build detailed client profile
        3. Meetings Agent will process any available meeting data
        4. Actionable Insights Agent will generate recommendations
        """