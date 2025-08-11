#!/usr/bin/env python3
"""
Test script for the new Natural Conversational Agent
Tests the free-flowing conversation approach with "Zulu.riverside" example
"""

import asyncio
import json
from agents.natural_conversational_agent import NaturalConversationalAgent
from database.db_manager import DatabaseManager

async def test_natural_conversation():
    """Test the natural conversational agent with realistic interactions"""
    
    # Initialize the agent
    db_manager = DatabaseManager("ks_onboarding.db")
    agent = NaturalConversationalAgent(db_manager)
    
    print("=== Testing Natural Conversational Agent ===")
    print("This test demonstrates the free-flowing conversation approach\n")
    
    # Start conversation
    print("🚀 Starting conversation...")
    session_id = "test_natural_session_001"
    start_result = await agent.start_conversation(session_id)
    
    print(f"\n🤖 Agent: {start_result['message']}")
    print(f"📊 Completion: {start_result['completion_percentage']:.1f}%")
    print(f"📋 Info collected: {json.dumps(start_result['client_info'], indent=2)}")
    
    # Test messages that should flow naturally
    test_messages = [
        "Hi there! My company is Zulu.riverside and we're in the IT industry",
        "hello?",  # This should be handled naturally now
        "are you there?",  # This too
        "We're facing challenges with our legacy systems and need to modernize our infrastructure",
        "Our current tech stack includes Java, MySQL, and some old mainframe systems",
        "We have a team of about 15 developers and we're located in San Francisco",
        "The project timeline is flexible but we'd like to complete it within 12 months",
        "Our budget is around $500K for this modernization project"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"👤 User: {message}")
        
        result = await agent.process_message(session_id, message)
        
        print(f"🤖 Agent: {result['message']}")
        print(f"📊 Completion: {result['completion_percentage']:.1f}%")
        
        if result['client_info']:
            print(f"📋 Info collected: {json.dumps(result['client_info'], indent=2)}")
        
        if result['missing_fields']:
            print(f"❓ Missing: {', '.join(result['missing_fields'])}")
        
        if result['is_complete']:
            print("✅ Conversation completed!")
            break
        
        print("\n" + "-"*50)
    
    # Final status check
    print("\n=== Final Status ===")
    final_status = agent.get_session_status(session_id)
    print(f"📊 Final completion: {final_status['completion_percentage']:.1f}%")
    print(f"✅ Complete: {final_status['is_complete']}")
    print(f"💬 Total messages: {final_status['message_count']}")
    print(f"📋 Final info: {json.dumps(final_status['client_info'], indent=2)}")
    
    print("\n🎉 Test completed! The agent should now handle conversations more naturally.")
    print("Key improvements:")
    print("- LLM has full conversational freedom")
    print("- Natural responses to clarifying questions like 'hello?' and 'are you there?'")
    print("- Information extraction happens organically")
    print("- No rigid stage-based progression")
    print("- Higher temperature for more natural responses")

if __name__ == "__main__":
    asyncio.run(test_natural_conversation())