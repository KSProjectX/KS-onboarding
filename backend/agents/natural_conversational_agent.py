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
3. Keep responses concise and focused (2-3 sentences max)
4. Ask only 1-2 specific questions per response
5. Be helpful and supportive throughout

You're trying to understand their:
- Company and industry
- Main business challenges or problems they're facing
- Current technology setup
- Project timeline and budget considerations
- Team structure and location
- Contact preferences

But approach this organically through conversation, not as a checklist. Let the conversation evolve naturally while staying focused on understanding how K-Square can help them succeed.

Be conversational, warm, and professional. Keep responses brief but engaging.
"""
    
    async def start_conversation(self, session_id: str) -> Dict[str, Any]:
        """Start a new conversation session"""
        session = ConversationSession(session_id=session_id)
        self.sessions[session_id] = session
        
        # Generate a natural, welcoming opening message
        opening_prompt = ChatPromptTemplate.from_template(
            self.system_prompt + 
            "\n\nGenerate ONLY a warm, welcoming opening message to start the conversation. "
            "Be friendly and set a positive tone for learning about their business needs. "
            "Return ONLY the message text that should be sent to the client, without any "
            "meta-commentary, notes, or explanations. Just the direct message."
        )
        
        chain = opening_prompt | self.llm
        
        try:
            response = await chain.ainvoke({})
            
            # Clean the response - extract only the actual message
            clean_message = self._extract_clean_message(response)
            
            # Add to conversation history
            session.messages.append({
                "role": "assistant",
                "content": clean_message,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "session_id": session_id,
                "message": clean_message,
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
    
    def _extract_clean_message(self, raw_response: str) -> str:
        """Extract clean message from LLM response, removing meta-commentary and enforcing brevity"""
        try:
            # Convert to string if it's not already
            response_text = str(raw_response)
            
            # Look for common patterns that indicate meta-commentary
            lines = response_text.split('\n')
            clean_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines
                if not line:
                    continue
                # Skip lines that look like meta-commentary
                if any(pattern in line.lower() for pattern in [
                    'notes on why', 'approach was chosen', 'would you like me to',
                    '**notes', '---', 'this approach', 'why this', 'adjust this message',
                    'generate a', 'response that', 'i\'m particularly interested',
                    'it sounds like', 'that\'s really', 'fantastic!', 'wow,'
                ]):
                    break  # Stop processing when we hit meta-commentary
                # Skip lines that start with asterisks (bullet points in explanations)
                if line.startswith('*') or line.startswith('-'):
                    continue
                # Add valid message lines
                clean_lines.append(line)
            
            # Join the clean lines
            clean_message = ' '.join(clean_lines).strip()
            
            # Remove quotes if the entire message is wrapped in quotes
            if clean_message.startswith('"') and clean_message.endswith('"'):
                clean_message = clean_message[1:-1].strip()
            
            # Enforce word limit (50 words max)
            words = clean_message.split()
            if len(words) > 50:
                # Keep first 45 words and add a question
                clean_message = ' '.join(words[:45])
                # Ensure it ends with a question if it doesn't already
                if not clean_message.endswith('?'):
                    clean_message += "?"
            
            # Remove excessive enthusiasm and redundant phrases
            clean_message = clean_message.replace('really ', '').replace('fantastic! ', '').replace('That\'s ', '')
            clean_message = clean_message.replace('It sounds like ', '').replace('I\'m particularly interested in ', '')
            
            # Fallback to a simple default if cleaning failed
            if not clean_message or len(clean_message) < 10:
                clean_message = "Hello! What brings you to K-Square today?"
            
            return clean_message
            
        except Exception as e:
            logger.error(f"Error cleaning message: {e}")
            return "Hello! What brings you to K-Square today?"
    
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
            "response": response,
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
            
Generate a brief, focused response that:
            1. Acknowledges what the user said (1 sentence)
            2. Asks 1-2 specific follow-up questions to gather missing info
            3. Keeps total response under 50 words
            4. Prioritizes the most important missing information
            
If completion is above 80%, focus on confirming details and next steps.
            Otherwise, ask targeted questions about the highest priority missing fields.
            
Be friendly but concise. No lengthy explanations or multiple topics."""
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