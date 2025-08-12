import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ClientInfo(BaseModel):
    """Structured client information model"""
    company_name: Optional[str] = Field(None, description="Company name")
    industry: Optional[str] = Field(None, description="Industry sector")
    problem_statement: Optional[str] = Field(None, description="Main business problem")
    tech_stack: Optional[List[str]] = Field(None, description="Current technology stack")
    timeline: Optional[str] = Field(None, description="Project timeline")
    budget: Optional[str] = Field(None, description="Project budget")
    team_size: Optional[int] = Field(None, description="Team size")
    location: Optional[str] = Field(None, description="Company location")
    stakeholders: Optional[List[Dict[str, str]]] = Field(None, description="Key stakeholders")
    completeness_score: float = Field(0.0, description="Information completeness score")

class ConversationState(BaseModel):
    """State for the conversation graph"""
    messages: List[Dict[str, str]] = Field(default_factory=list)
    client_info: ClientInfo = Field(default_factory=ClientInfo)
    conversation_stage: str = Field(default="greeting")
    questions_asked: List[str] = Field(default_factory=list)
    is_complete: bool = Field(default=False)
    session_id: str = Field(default="")

class ConversationalSetupAgent:
    """Conversational AI agent for client onboarding using LangGraph and Ollama"""
    
    def __init__(self, db_manager, model_name: str = "gemma3:latest"):
        self.db_manager = db_manager
        self.name = "Conversational Setup Agent"
        self.model_name = model_name
        self.llm = Ollama(model=model_name, temperature=0.7)
        self.json_parser = JsonOutputParser(pydantic_object=ClientInfo)
        self.conversation_graph = self._build_conversation_graph()
        
    def _build_conversation_graph(self) -> StateGraph:
        """Build the conversation flow graph using LangGraph"""
        graph = StateGraph(ConversationState)
        
        # Add nodes
        graph.add_node("greeting", self._greeting_node)
        graph.add_node("gather_basic_info", self._gather_basic_info_node)
        graph.add_node("gather_technical_info", self._gather_technical_info_node)
        graph.add_node("gather_project_details", self._gather_project_details_node)
        graph.add_node("clarify_missing_info", self._clarify_missing_info_node)
        graph.add_node("summarize_and_confirm", self._summarize_and_confirm_node)
        graph.add_node("complete_setup", self._complete_setup_node)
        
        # Add edges
        graph.add_edge("greeting", "gather_basic_info")
        graph.add_edge("gather_basic_info", "gather_technical_info")
        graph.add_edge("gather_technical_info", "gather_project_details")
        graph.add_edge("gather_project_details", "clarify_missing_info")
        graph.add_edge("clarify_missing_info", "summarize_and_confirm")
        graph.add_edge("summarize_and_confirm", "complete_setup")
        graph.add_edge("complete_setup", END)
        
        # Set entry point
        graph.set_entry_point("greeting")
        
        return graph.compile()
    
    async def start_conversation(self, session_id: str) -> Dict[str, Any]:
        """Start a new conversation session"""
        initial_state = ConversationState(session_id=session_id)
        
        # Start with greeting
        greeting_message = "Hello! I'm here to help you set up your K-Square programme. Let's start by getting to know your company. What's your company name and what industry are you in?"
        
        initial_state.messages.append({
            "role": "assistant",
            "content": greeting_message,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "started",
            "session_id": session_id,
            "message": greeting_message,
            "stage": initial_state.conversation_stage,
            "state": initial_state.dict()
        }
    
    def _is_conversational_message(self, message: str) -> bool:
        """Check if the message is a conversational/clarifying message rather than informational"""
        conversational_patterns = [
            "hello", "hi", "hey", "are you there", "can you hear me", "?", 
            "yes", "no", "ok", "okay", "thanks", "thank you", "what", "huh",
            "sorry", "excuse me", "wait", "hold on", "i don't understand",
            "can you repeat", "what did you say", "pardon", "come again"
        ]
        
        message_lower = message.lower().strip()
        
        # Check for very short messages (likely conversational)
        if len(message_lower) <= 3:
            return True
            
        # Check for question marks without substantial content
        if "?" in message and len(message_lower.replace("?", "").strip()) <= 10:
            return True
            
        # Check for conversational patterns
        for pattern in conversational_patterns:
            if pattern in message_lower:
                return True
                
        return False

    async def _extract_information_with_llm(self, user_message: str, extraction_type: str, current_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Use LLM to extract information from user message"""
        extraction_prompts = {
            "company_and_industry": """
            Extract the company name and industry from the user's message. Be flexible and natural - company names can be in any language, format, or style.
            
            User message: "{message}"
            
            Return a JSON object with:
            - company_name: The company name (exactly as mentioned, preserve original formatting)
            - industry: The industry if mentioned (or null if not clear)
            
            Examples:
            - "Hi, my company is Weird-Co and we're in IT" -> {{"company_name": "Weird-Co", "industry": "IT"}}
            - "We are 株式会社テスト in technology" -> {{"company_name": "株式会社テスト", "industry": "technology"}}
            - "I work at ABC-123 Corp" -> {{"company_name": "ABC-123 Corp", "industry": null}}
            """,
            "problem_statement": """
            Extract the main business problem or challenge from the user's message. Be comprehensive and preserve the user's own words.
            
            User message: "{message}"
            
            Return a JSON object with:
            - problem_statement: The main challenge or problem described
            """,
            "tech_stack": """
            Extract technology stack, tools, platforms, and systems from the user's message. Be flexible with formats and naming.
            
            User message: "{message}"
            
            Return a JSON object with:
            - tech_stack: Array of technologies mentioned
            """,
            "project_details": """
            Extract project timeline, budget, team size, and other project details from the user's message.
            
            User message: "{message}"
            
            Return a JSON object with:
            - timeline: Project timeline if mentioned
            - budget: Budget information if mentioned  
            - team_size: Team size if mentioned (as integer)
            - location: Company location if mentioned
            """
        }
        
        prompt_template = extraction_prompts.get(extraction_type, "")
        if not prompt_template:
            return {}
            
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            result = await chain.ainvoke({"message": user_message})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return {}
    
    async def process_message(self, session_id: str, user_message: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process user message and continue conversation"""
        try:
            # Reconstruct state
            state = ConversationState(**current_state)
            
            # Add user message
            state.messages.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if this is a conversational message that doesn't contain information
            if self._is_conversational_message(user_message):
                # Handle conversational messages without progressing stages
                if any(word in user_message.lower() for word in ["hello", "hi", "hey", "are you there"]):
                    if state.conversation_stage == "greeting":
                        response_message = "Hello! I'm here to help you set up your K-Square programme. Let's start by getting to know your company. What's your company name and what industry are you in?"
                    elif state.conversation_stage == "gather_basic_info":
                        response_message = "Yes, I'm here! I was asking about the specific challenges or problems you're facing that you'd like to address. Could you tell me more about that?"
                    elif state.conversation_stage == "gather_technical_info":
                        response_message = "I'm here! I need to understand your current technology setup. What systems, platforms, and tools are you currently using?"
                    elif state.conversation_stage == "gather_project_details":
                        response_message = "Yes, I'm listening! I was asking about your preferred timeline and budget for implementing this solution. Could you share those details?"
                    else:
                        response_message = "I'm here and ready to help! What information can I assist you with?"
                elif "?" in user_message and len(user_message.strip()) <= 10:
                    response_message = "I'm here! Please let me know what information you'd like to share or if you have any questions about the setup process."
                else:
                    response_message = "I'm listening! Please continue with the information I requested, or let me know if you have any questions."
            else:
                # Process informational messages based on current stage
                response_message = ""
                
                if state.conversation_stage == "greeting":
                    # Use LLM to extract company name and industry
                    extracted_info = await self._extract_information_with_llm(user_message, "company_and_industry")
                    
                    if extracted_info.get("company_name"):
                        state.client_info.company_name = extracted_info["company_name"]
                    if extracted_info.get("industry"):
                        state.client_info.industry = extracted_info["industry"]
                    
                    # Generate appropriate response
                    if state.client_info.company_name and state.client_info.industry:
                        state.conversation_stage = "gather_basic_info"
                        response_message = f"Great! So you're {state.client_info.company_name} in the {state.client_info.industry} industry. Now, could you tell me about the specific challenges or problems you're facing that you'd like to address?"
                    elif state.client_info.company_name:
                        response_message = f"Thank you, {state.client_info.company_name}! What industry are you in?"
                    elif state.client_info.industry:
                        response_message = f"Great! I see you're in the {state.client_info.industry} industry. What's your company name?"
                    else:
                        response_message = "I'd love to learn more about your company. Could you tell me your company name and what industry you're in?"
                
                elif state.conversation_stage == "gather_basic_info":
                    # Use LLM to extract problem statement
                    extracted_info = await self._extract_information_with_llm(user_message, "problem_statement")
                    if extracted_info.get("problem_statement"):
                        state.client_info.problem_statement = extracted_info["problem_statement"]
                    else:
                        state.client_info.problem_statement = user_message  # Fallback to full message
                    
                    state.conversation_stage = "gather_technical_info"
                    response_message = "Thank you for explaining your challenges. Now I need to understand your current technology setup. What systems, platforms, and tools are you currently using?"
                
                elif state.conversation_stage == "gather_technical_info":
                    # Use LLM to extract tech stack
                    extracted_info = await self._extract_information_with_llm(user_message, "tech_stack")
                    if extracted_info.get("tech_stack"):
                        state.client_info.tech_stack = extracted_info["tech_stack"]
                    else:
                        # Fallback to simple splitting
                        state.client_info.tech_stack = [tech.strip() for tech in user_message.split(',')]
                    
                    state.conversation_stage = "gather_project_details"
                    response_message = "Excellent! I understand your technology infrastructure. What's your preferred timeline and budget for implementing this solution?"
                
                elif state.conversation_stage == "gather_project_details":
                    # Use LLM to extract project details
                    extracted_info = await self._extract_information_with_llm(user_message, "project_details")
                    
                    if extracted_info.get("timeline"):
                        state.client_info.timeline = extracted_info["timeline"]
                    if extracted_info.get("budget"):
                        state.client_info.budget = extracted_info["budget"]
                    if extracted_info.get("team_size"):
                        state.client_info.team_size = extracted_info["team_size"]
                    if extracted_info.get("location"):
                        state.client_info.location = extracted_info["location"]
                    
                    # If no specific details were extracted, store the full message as timeline context
                    if not any([extracted_info.get("timeline"), extracted_info.get("budget")]):
                        state.client_info.timeline = user_message
                    
                    state.conversation_stage = "clarify_missing_info"
                    
                    # Calculate completeness
                    state.client_info.completeness_score = self._calculate_completeness(state.client_info)
                    
                    response_message = "Thank you for the project details. Let me check if we have all the information needed to proceed."
                
                elif state.conversation_stage == "clarify_missing_info":
                    # Use LLM to extract remaining details
                    extracted_info = await self._extract_information_with_llm(user_message, "project_details")
                    
                    if extracted_info.get("team_size") and not state.client_info.team_size:
                        state.client_info.team_size = extracted_info["team_size"]
                    if extracted_info.get("location") and not state.client_info.location:
                        state.client_info.location = extracted_info["location"]
                    
                    # If no structured extraction worked, try to infer from the message
                    if not state.client_info.team_size and not state.client_info.location:
                        # Store the message as additional context
                        if not state.client_info.location:
                            state.client_info.location = user_message
                    
                    state.conversation_stage = "summarize_and_confirm"
                    
                    # Calculate completeness
                    state.client_info.completeness_score = self._calculate_completeness(state.client_info)
                    
                    response_message = f"Perfect! Let me summarize what I've gathered:\n\n" \
                                     f"Company: {state.client_info.company_name}\n" \
                                     f"Industry: {state.client_info.industry}\n" \
                                     f"Challenge: {state.client_info.problem_statement}\n" \
                                     f"Tech Stack: {', '.join(state.client_info.tech_stack) if state.client_info.tech_stack else 'Not specified'}\n" \
                                     f"Timeline: {state.client_info.timeline}\n\n" \
                                     f"Is this information correct? If yes, I'll proceed to set up your K-Square programme."
                
                elif state.conversation_stage == "summarize_and_confirm":
                    if "yes" in user_message.lower() or "correct" in user_message.lower():
                        state.conversation_stage = "complete"
                        state.is_complete = True
                        response_message = "Excellent! I have all the information needed. I'm now setting up your K-Square programme with a customized plan tailored to your specific needs. Your onboarding strategy is being prepared!"
                        
                        # Save conversation and create profile
                        await self._save_conversation_as_meeting(state)
                        await self._create_client_profile(state)
                    else:
                        state.conversation_stage = "gather_basic_info"
                        response_message = "No problem! Let's go through the information again. What would you like to correct?"
            
            # Add assistant response
            state.messages.append({
                "role": "assistant",
                "content": response_message,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "response": response_message,
                "conversation_id": session_id,
                "stage": state.conversation_stage,
                "is_complete": state.is_complete,
                "client_info": state.client_info.dict(),
                "completeness_score": state.client_info.completeness_score,
                "state": state.dict()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "status": "error",
                "message": "I apologize, but I encountered an error. Could you please try again?",
                "error": str(e)
            }
    
    async def _greeting_node(self, state: ConversationState) -> ConversationState:
        """Initial greeting and introduction"""
        prompt = ChatPromptTemplate.from_template(
            "You are a friendly AI assistant helping with client onboarding. "
            "Greet the user warmly and explain that you'll be gathering information "
            "about their company and project needs. Ask for their company name to start."
        )
        
        response = await self.llm.ainvoke(prompt.format())
        
        state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        state.conversation_stage = "gather_basic_info"
        return state
    
    async def _gather_basic_info_node(self, state: ConversationState) -> ConversationState:
        """Gather basic company information"""
        user_message = state.messages[-1]["content"]
        
        # Extract company info from user message
        extraction_prompt = ChatPromptTemplate.from_template(
            "Extract company information from this message: '{message}'"
            "Return JSON with fields: company_name, industry, location if mentioned."
            "If information is not provided, set field to null."
        )
        
        extraction_response = await self.llm.ainvoke(extraction_prompt.format(message=user_message))
        
        try:
            extracted_info = json.loads(extraction_response)
            if extracted_info.get("company_name"):
                state.client_info.company_name = extracted_info["company_name"]
            if extracted_info.get("industry"):
                state.client_info.industry = extracted_info["industry"]
            if extracted_info.get("location"):
                state.client_info.location = extracted_info["location"]
        except json.JSONDecodeError:
            logger.warning("Could not parse extracted information as JSON")
        
        # Generate next question
        next_question_prompt = ChatPromptTemplate.from_template(
            "Based on the information gathered so far: {client_info}, "
            "ask the next logical question to gather basic company information. "
            "Focus on industry, company size, or location if not yet provided. "
            "Be conversational and friendly."
        )
        
        response = await self.llm.ainvoke(
            next_question_prompt.format(client_info=state.client_info.dict())
        )
        
        state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if we have enough basic info to move on
        if state.client_info.company_name and state.client_info.industry:
            state.conversation_stage = "gather_technical_info"
        
        return state
    
    async def _gather_technical_info_node(self, state: ConversationState) -> ConversationState:
        """Gather technical information and problem statement"""
        user_message = state.messages[-1]["content"]
        
        # Extract technical info
        extraction_prompt = ChatPromptTemplate.from_template(
            "Extract technical and problem information from: '{message}'"
            "Return JSON with fields: problem_statement, tech_stack (as array), team_size."
            "If information is not provided, set field to null."
        )
        
        extraction_response = await self.llm.ainvoke(extraction_prompt.format(message=user_message))
        
        try:
            extracted_info = json.loads(extraction_response)
            if extracted_info.get("problem_statement"):
                state.client_info.problem_statement = extracted_info["problem_statement"]
            if extracted_info.get("tech_stack"):
                state.client_info.tech_stack = extracted_info["tech_stack"]
            if extracted_info.get("team_size"):
                state.client_info.team_size = extracted_info["team_size"]
        except json.JSONDecodeError:
            logger.warning("Could not parse technical information as JSON")
        
        # Generate next question
        next_question_prompt = ChatPromptTemplate.from_template(
            "Based on the information gathered: {client_info}, "
            "ask about technical challenges, current systems, or team structure. "
            "Be specific and helpful."
        )
        
        response = await self.llm.ainvoke(
            next_question_prompt.format(client_info=state.client_info.dict())
        )
        
        state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if we have enough technical info
        if state.client_info.problem_statement and state.client_info.tech_stack:
            state.conversation_stage = "gather_project_details"
        
        return state
    
    async def _gather_project_details_node(self, state: ConversationState) -> ConversationState:
        """Gather project timeline and budget information"""
        user_message = state.messages[-1]["content"]
        
        # Extract project details
        extraction_prompt = ChatPromptTemplate.from_template(
            "Extract project details from: '{message}'"
            "Return JSON with fields: timeline, budget, stakeholders (as array of objects with name and role)."
            "If information is not provided, set field to null."
        )
        
        extraction_response = await self.llm.ainvoke(extraction_prompt.format(message=user_message))
        
        try:
            extracted_info = json.loads(extraction_response)
            if extracted_info.get("timeline"):
                state.client_info.timeline = extracted_info["timeline"]
            if extracted_info.get("budget"):
                state.client_info.budget = extracted_info["budget"]
            if extracted_info.get("stakeholders"):
                state.client_info.stakeholders = extracted_info["stakeholders"]
        except json.JSONDecodeError:
            logger.warning("Could not parse project details as JSON")
        
        # Generate next question or move to clarification
        next_question_prompt = ChatPromptTemplate.from_template(
            "Based on the project information gathered: {client_info}, "
            "ask about timeline, budget, or key stakeholders if not yet provided. "
            "Be professional and understanding about budget sensitivity."
        )
        
        response = await self.llm.ainvoke(
            next_question_prompt.format(client_info=state.client_info.dict())
        )
        
        state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        state.conversation_stage = "clarify_missing_info"
        return state
    
    async def _clarify_missing_info_node(self, state: ConversationState) -> ConversationState:
        """Clarify any missing critical information"""
        # Calculate completeness score
        state.client_info.completeness_score = self._calculate_completeness(state.client_info)
        
        if state.client_info.completeness_score >= 0.8:
            state.conversation_stage = "summarize_and_confirm"
        else:
            # Ask for missing critical information
            missing_fields = self._identify_missing_fields(state.client_info)
            
            clarification_prompt = ChatPromptTemplate.from_template(
                "The following information is still needed: {missing_fields}. "
                "Ask for the most important missing information in a friendly way."
            )
            
            response = await self.llm.ainvoke(
                clarification_prompt.format(missing_fields=missing_fields)
            )
            
            state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def _summarize_and_confirm_node(self, state: ConversationState) -> ConversationState:
        """Summarize gathered information and ask for confirmation"""
        summary_prompt = ChatPromptTemplate.from_template(
            "Summarize the following client information in a clear, organized way: {client_info}. "
            "Ask the user to confirm if this information is correct and if they'd like to add anything."
        )
        
        response = await self.llm.ainvoke(
            summary_prompt.format(client_info=state.client_info.dict())
        )
        
        state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        state.conversation_stage = "complete_setup"
        return state
    
    async def _complete_setup_node(self, state: ConversationState) -> ConversationState:
        """Complete the setup process"""
        completion_prompt = ChatPromptTemplate.from_template(
            "Thank the user for providing the information and let them know that "
            "their client profile has been created and they can now proceed to "
            "explore insights and recommendations. Be warm and professional."
        )
        
        response = await self.llm.ainvoke(completion_prompt.format())
        
        state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        state.is_complete = True
        return state
    
    def _calculate_completeness(self, client_info: ClientInfo) -> float:
        """Calculate information completeness score"""
        required_fields = [
            "company_name", "industry", "problem_statement", 
            "tech_stack", "timeline"
        ]
        
        completed_fields = 0
        for field in required_fields:
            value = getattr(client_info, field)
            if value is not None and value != "" and value != []:
                completed_fields += 1
        
        return completed_fields / len(required_fields)
    
    def _identify_missing_fields(self, client_info: ClientInfo) -> List[str]:
        """Identify missing critical fields"""
        required_fields = {
            "company_name": "Company name",
            "industry": "Industry",
            "problem_statement": "Problem statement",
            "tech_stack": "Technology stack",
            "timeline": "Project timeline"
        }
        
        missing = []
        for field, label in required_fields.items():
            value = getattr(client_info, field)
            if value is None or value == "" or value == []:
                missing.append(label)
        
        return missing
    
    async def _save_conversation_as_meeting(self, state: ConversationState):
        """Save the conversation as a meeting record"""
        try:
            # Create transcript from messages
            transcript = "\n\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in state.messages
            ])
            
            # Analyze sentiment
            sentiment_score, sentiment_category = self.db_manager.analyze_sentiment(transcript)
            
            # Create action items based on gathered information
            action_items = [
                "Review and validate client profile information",
                "Prepare initial project recommendations",
                "Schedule follow-up meeting for project planning"
            ]
            
            # Calculate engagement metrics
            engagement_metrics = {
                "message_count": len(state.messages),
                "conversation_duration": "estimated_30_minutes",
                "information_completeness": state.client_info.completeness_score,
                "interaction_type": "conversational_onboarding"
            }
            
            # Save to database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO meetings (client_name, transcript, action_items, 
                                    engagement_metrics, sentiment_score, sentiment_category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                state.client_info.company_name,
                transcript,
                json.dumps(action_items),
                json.dumps(engagement_metrics),
                sentiment_score,
                sentiment_category
            ))
            
            conn.commit()
            logger.info(f"Conversation saved as meeting for {state.client_info.company_name}")
            
        except Exception as e:
            logger.error(f"Error saving conversation as meeting: {e}")
    
    async def _create_client_profile(self, state: ConversationState):
        """Create client profile from gathered information"""
        try:
            # Convert ClientInfo to profile format
            profile_data = {
                "id": f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "company_name": state.client_info.company_name,
                "industry": state.client_info.industry,
                "founding_year": None,  # Not gathered in conversation
                "company_size": f"Team of {state.client_info.team_size}" if state.client_info.team_size else "Unknown",
                "regions": [state.client_info.location] if state.client_info.location else ["Unknown"],
                "stakeholders": state.client_info.stakeholders or [],
                "tech_stack": state.client_info.tech_stack or [],
                "primary_challenge": "Digital Transformation",
                "problem_statement": state.client_info.problem_statement,
                "completeness_score": int(state.client_info.completeness_score * 100),
                "insights": {
                    "market_position": "To be determined",
                    "growth_potential": "Medium",
                    "risk_factors": ["Implementation complexity"],
                    "recommendations": ["Conduct detailed technical assessment"]
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "profile_source": "conversational_agent",
                "conversation_metadata": {
                    "session_id": state.session_id,
                    "message_count": len(state.messages),
                    "timeline": state.client_info.timeline,
                    "budget": state.client_info.budget
                }
            }
            
            # Save profile to database
            self.db_manager.save_client_profile(
                state.client_info.company_name,
                profile_data
            )
            
            logger.info(f"Client profile created for {state.client_info.company_name}")
            
        except Exception as e:
            logger.error(f"Error creating client profile: {e}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status - for ConversationalSetupAgent, we need to reconstruct from database or return default state"""
        try:
            # Since ConversationalSetupAgent doesn't maintain session state in memory,
            # we'll return a default state structure that process_message can work with
            default_state = ConversationState(session_id=session_id)
            
            return {
                "session_id": session_id,
                "messages": default_state.messages,
                "client_info": default_state.client_info.dict(),
                "conversation_stage": default_state.conversation_stage,
                "questions_asked": default_state.questions_asked,
                "is_complete": default_state.is_complete
            }
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {"error": f"Failed to get session status: {str(e)}"}