import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ClientInfo(BaseModel):
    """Required client information to be collected"""
    company_name: Optional[str] = Field(None, description="Company name")
    industry: Optional[str] = Field(None, description="Industry sector")
    problem_statement: Optional[str] = Field(None, description="Main business problem or challenge")
    tech_stack: Optional[List[str]] = Field(None, description="Current technology stack")
    timeline: Optional[str] = Field(None, description="Project timeline")
    budget: Optional[str] = Field(None, description="Project budget range")
    team_size: Optional[int] = Field(None, description="Team size")
    location: Optional[str] = Field(None, description="Company location")
    contact_info: Optional[Dict[str, str]] = Field(None, description="Contact information")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.dict().items() if v is not None}
    
    def completion_percentage(self) -> float:
        """Calculate how much information we have collected"""
        total_fields = 9  # Total number of fields
        filled_fields = len([v for v in self.dict().values() if v is not None])
        return (filled_fields / total_fields) * 100
    
    def missing_fields(self) -> List[str]:
        """Get list of missing field names"""
        return [k for k, v in self.dict().items() if v is None]

class ConversationSession(BaseModel):
    """Conversation session state"""
    session_id: str
    messages: List[Dict[str, str]] = Field(default_factory=list)
    client_info: ClientInfo = Field(default_factory=ClientInfo)
    is_complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

class NaturalConversationalAgent:
    """A natural, free-flowing conversational agent that collects client information organically"""
    
    def __init__(self, db_manager, model_name: str = "gemma3:latest"):
        self.db_manager = db_manager
        self.name = "Natural Conversational Agent"
        self.model_name = model_name
        self.llm = Ollama(model=model_name, temperature=0.8)  # Higher temperature for more natural responses
        self.sessions: Dict[str, ConversationSession] = {}
        
        # Core system prompt that gives the LLM freedom while maintaining purpose
        self.system_prompt = """
You are a friendly, intelligent business consultant helping clients with their K-Square onboarding process. 

Your goal is to have a natural, engaging conversation while gradually learning about their business needs. You should:

1. Be genuinely curious and interested in their business
2. Ask follow-up questions naturally based on what they tell you
3. Share relevant insights or experiences when appropriate
4. Keep the conversation flowing smoothly - don't interrogate
5. Be helpful and supportive throughout

You're trying to understand their:
- Company and industry
- Main business challenges or problems they're facing
- Current technology setup
- Project timeline and budget considerations
- Team structure and location
- Contact preferences

But approach this organically through conversation, not as a checklist. Let the conversation evolve naturally while staying focused on understanding how K-Square can help them succeed.

Be conversational, warm, and professional. Show genuine interest in their business and challenges.
"""
    
    async def start_conversation(self, session_id: str) -> Dict[str, Any]:
        """Start a new conversation session"""
        session = ConversationSession(session_id=session_id)
        self.sessions[session_id] = session
        
        # Generate a natural, welcoming opening message
        opening_prompt = ChatPromptTemplate.from_template(
            self.system_prompt + 
            "\n\nGenerate a warm, welcoming opening message to start the conversation. "
            "Be friendly and set a positive tone for learning about their business needs."
        )
        
        chain = opening_prompt | self.llm
        
        try:
            response = await chain.ainvoke({})
            
            # Add to conversation history
            session.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "session_id": session_id,
                "message": response,
                "client_info": session.client_info.to_dict(),
                "completion_percentage": session.client_info.completion_percentage(),
                "is_complete": session.is_complete
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return {
                "session_id": session_id,
                "message": "Hello! I'm excited to learn about your business and how K-Square can help you succeed. What brings you here today?",
                "client_info": {},
                "completion_percentage": 0,
                "is_complete": False
            }
    
    async def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process user message and generate natural response"""
        if session_id not in self.sessions:
            return await self.start_conversation(session_id)
        
        session = self.sessions[session_id]
        
        # Add user message to history
        session.messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract any new information from the user's message
        await self._extract_information(session, user_message)
        
        # Generate natural response based on conversation context
        response = await self._generate_response(session, user_message)
        
        # Add assistant response to history
        session.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if we have enough information to complete
        completion_percentage = session.client_info.completion_percentage()
        if completion_percentage >= 80 and not session.is_complete:
            session.is_complete = True
            # Save the completed session
            await self._save_session(session)
        
        return {
            "session_id": session_id,
            "message": response,
            "client_info": session.client_info.to_dict(),
            "completion_percentage": completion_percentage,
            "missing_fields": session.client_info.missing_fields(),
            "is_complete": session.is_complete
        }
    
    async def _extract_information(self, session: ConversationSession, user_message: str):
        """Extract any relevant information from user message and update client info"""
        current_info = session.client_info.to_dict()
        
        extraction_prompt = ChatPromptTemplate.from_template(
            """Extract any business information from this user message and return it as JSON.
            
Current information we have: {current_info}
            
User message: "{user_message}"
            
Extract any of these fields if mentioned (return null for fields not mentioned):
            - company_name: Company name (preserve exact formatting)
            - industry: Industry or business sector
            - problem_statement: Business problem, challenge, or goal
            - tech_stack: Technologies, tools, platforms (as array)
            - timeline: Project timeline or deadlines
            - budget: Budget information or range
            - team_size: Number of team members (as integer)
            - location: Company or team location
            - contact_info: Contact details like email, phone (as object)
            
Only extract information that is clearly stated. Don't infer or assume.
            Return valid JSON only."""
        )
        
        chain = extraction_prompt | self.llm | JsonOutputParser()
        
        try:
            extracted = await chain.ainvoke({
                "current_info": json.dumps(current_info),
                "user_message": user_message
            })
            
            # Update client info with extracted data
            if isinstance(extracted, dict):
                for key, value in extracted.items():
                    if value is not None and hasattr(session.client_info, key):
                        setattr(session.client_info, key, value)
                        
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
    
    async def _generate_response(self, session: ConversationSession, user_message: str) -> str:
        """Generate a natural, contextual response"""
        # Build conversation context
        recent_messages = session.messages[-6:]  # Last 6 messages for context
        conversation_history = "\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in recent_messages
        ])
        
        current_info = session.client_info.to_dict()
        missing_fields = session.client_info.missing_fields()
        completion_percentage = session.client_info.completion_percentage()
        
        response_prompt = ChatPromptTemplate.from_template(
            self.system_prompt + 
            """
            
Conversation so far:
            {conversation_history}
            
User just said: "{user_message}"
            
Current information collected: {current_info}
            Missing information: {missing_fields}
            Completion: {completion_percentage}%
            
Generate a natural, engaging response that:
            1. Responds appropriately to what the user just said
            2. Shows genuine interest and understanding
            3. Naturally guides the conversation toward learning more (if needed)
            4. Feels like a real business conversation, not an interview
            
If completion is above 80%, focus on summarizing and confirming the information.
            Otherwise, continue the natural flow while gently exploring missing areas.
            
Be conversational, helpful, and authentic."""
        )
        
        chain = response_prompt | self.llm
        
        try:
            response = await chain.ainvoke({
                "conversation_history": conversation_history,
                "user_message": user_message,
                "current_info": json.dumps(current_info),
                "missing_fields": missing_fields,
                "completion_percentage": completion_percentage
            })
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I appreciate you sharing that with me. Could you tell me a bit more about your business and what you're hoping to achieve?"
    
    async def _save_session(self, session: ConversationSession):
        """Save completed session to database"""
        try:
            # Save conversation as meeting
            conversation_text = "\n\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in session.messages
            ])
            
            meeting_data = {
                "session_id": session.session_id,
                "transcript": conversation_text,
                "client_info": session.client_info.to_dict(),
                "created_at": session.created_at.isoformat(),
                "completion_percentage": session.client_info.completion_percentage()
            }
            
            # Save to database (implement based on your db_manager)
            # await self.db_manager.save_meeting(meeting_data)
            
            logger.info(f"Session {session.session_id} completed and saved")
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "client_info": session.client_info.to_dict(),
            "completion_percentage": session.client_info.completion_percentage(),
            "missing_fields": session.client_info.missing_fields(),
            "is_complete": session.is_complete,
            "message_count": len(session.messages)
        }