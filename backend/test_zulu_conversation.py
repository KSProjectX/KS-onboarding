#!/usr/bin/env python3
import requests
import json
import time

def test_zulu_conversation():
    base_url = "http://localhost:8001"
    
    # Start conversation
    print("Starting conversation...")
    start_response = requests.post(f"{base_url}/api/conversation/start")
    print(f"Start response: {start_response.status_code}")
    
    if start_response.status_code == 200:
        start_data = start_response.json()
        conversation_id = start_data.get('conversation_id') or start_data.get('session_id')
        print(f"Conversation ID: {conversation_id}")
        print(f"Initial response: {start_data.get('response', 'No response')}")
        
        # First message - company name
        print("\n=== First Message ===")
        message1 = "the name of my company is Zulu.riverside and we are into IT industry"
        print(f"Sending: {message1}")
        
        response1 = requests.post(
            f"{base_url}/api/conversation/message",
            json={"conversation_id": conversation_id, "message": message1}
        )
        
        print(f"Response status: {response1.status_code}")
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"Response: {data1.get('response', 'No response')}")
            print(f"Stage: {data1.get('stage', 'Unknown')}")
            print(f"Company extracted: {data1.get('client_info', {}).get('company_name', 'None')}")
            print(f"Industry extracted: {data1.get('client_info', {}).get('industry', 'None')}")
        else:
            print(f"Error: {response1.text}")
            return
        
        # Wait a bit
        time.sleep(2)
        
        # Second message - hello?
        print("\n=== Second Message ===")
        message2 = "hello?"
        print(f"Sending: {message2}")
        
        response2 = requests.post(
            f"{base_url}/api/conversation/message",
            json={"conversation_id": conversation_id, "message": message2}
        )
        
        print(f"Response status: {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"Response: {data2.get('response', 'No response')}")
            print(f"Stage: {data2.get('stage', 'Unknown')}")
        else:
            print(f"Error: {response2.text}")
            return
        
        # Wait a bit
        time.sleep(2)
        
        # Third message - are you there?
        print("\n=== Third Message ===")
        message3 = "are you there?"
        print(f"Sending: {message3}")
        
        response3 = requests.post(
            f"{base_url}/api/conversation/message",
            json={"conversation_id": conversation_id, "message": message3}
        )
        
        print(f"Response status: {response3.status_code}")
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"Response: {data3.get('response', 'No response')}")
            print(f"Stage: {data3.get('stage', 'Unknown')}")
        else:
            print(f"Error: {response3.text}")
            return
            
        # Check conversation status
        print("\n=== Conversation Status ===")
        status_response = requests.get(f"{base_url}/api/conversation/{conversation_id}/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"Full conversation state:")
            print(json.dumps(status_data, indent=2))
        else:
            print(f"Status check failed: {status_response.text}")
    else:
        print(f"Error starting conversation: {start_response.text}")

if __name__ == "__main__":
    test_zulu_conversation()