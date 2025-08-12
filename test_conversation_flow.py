#!/usr/bin/env python3
"""
Standalone test for the natural conversational agent
Tests the complete conversation flow and client registration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.agents.natural_conversational_agent import NaturalConversationalAgent
from backend.database.db_manager import DatabaseManager

async def test_conversation_flow():
    """Test the complete conversation flow"""
    print("=== Testing Natural Conversational Agent ===")
    print()
    
    # Initialize database manager
    print("1. Initializing database manager...")
    db_manager = DatabaseManager()
    print("   ✓ Database initialized")
    print()
    
    # Initialize the conversational agent
    print("2. Initializing natural conversational agent...")
    agent = NaturalConversationalAgent(db_manager)
    print("   ✓ Agent initialized")
    print()
    
    # Start a conversation
    print("3. Starting conversation...")
    session_id = "test_session_123"
    start_result = await agent.start_conversation(session_id)
    
    print(f"   Session ID: {start_result['session_id']}")
    print(f"   Opening message: {start_result['message']}")
    print(f"   Completion: {start_result['completion_percentage']}%")
    print(f"   Is complete: {start_result['is_complete']}")
    print()
    
    # Simulate a conversation
    print("4. Simulating conversation...")
    
    test_messages = [
        "Hi! I'm John from TechCorp, a software development company.",
        "We're in the fintech industry and we're struggling with scalability issues in our payment processing system.",
        "We're currently using Python with Django and PostgreSQL, but we're open to new technologies.",
        "We need to solve this within 6 months and have a budget of around $200,000.",
        "Our team has 15 developers and we're based in San Francisco."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"   User message {i}: {message}")
        
        response = await agent.process_message(session_id, message)
        
        print(f"   Bot response: {response['message']}")
        print(f"   Completion: {response['completion_percentage']}%")
        print(f"   Is complete: {response['is_complete']}")
        
        if response['client_info']:
            print(f"   Client info: {response['client_info']}")
        
        print()
        
        if response['is_complete']:
            print("   🎉 Conversation completed!")
            break
    
    # Check session status
    print("5. Checking final session status...")
    session_status = agent.get_session_status(session_id)
    print(f"   Session exists: {session_status.get('exists', 'Unknown')}")
    print(f"   Message count: {session_status.get('message_count', 'Unknown')}")
    print(f"   Final completion: {session_status.get('completion_percentage', 'Unknown')}%")
    print(f"   Final client info: {session_status.get('client_info', {})}")
    print(f"   Full session status: {session_status}")
    print()
    
    # Test database persistence (if implemented)
    print("6. Testing database operations...")
    try:
        # Try to save the session to database
        session = agent.sessions.get(session_id)
        if session:
            await agent._save_session(session)
            print("   ✓ Session saved to database")
        else:
            print("   ⚠ No session found to save")
    except Exception as e:
        print(f"   ⚠ Database save error: {e}")
    
    print()
    print("=== Test Complete ===")
    
    return start_result, session_status

if __name__ == "__main__":
    print("Starting conversation flow test...")
    print()
    
    try:
        result = asyncio.run(test_conversation_flow())
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)