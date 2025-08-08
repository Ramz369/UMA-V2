#!/usr/bin/env python3
"""
Test DeepSeek V3 API Connection
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_v3():
    """Test DeepSeek V3 API connection"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env file")
        return False
    
    print(f"🔑 API Key loaded: {api_key[:10]}...")
    
    # DeepSeek V3 API endpoint
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test payload for DeepSeek V3
    payload = {
        "model": "deepseek-chat",  # V3 model
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that tests API connections."
            },
            {
                "role": "user",
                "content": "Please respond with 'Connection successful!' if you receive this message."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    print("🔄 Testing DeepSeek V3 API connection...")
    print(f"📍 Endpoint: {url}")
    print(f"🤖 Model: deepseek-chat (V3)")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got a valid response
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"✅ Connection successful!")
                print(f"📝 Response: {content}")
                
                # Show usage stats if available
                if 'usage' in data:
                    print(f"📈 Tokens used: {data['usage'].get('total_tokens', 'N/A')}")
                
                return True
            else:
                print(f"⚠️ Unexpected response format: {json.dumps(data, indent=2)}")
                return False
                
        elif response.status_code == 401:
            print("❌ Authentication failed - Invalid API key")
            return False
            
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded - Try again later")
            return False
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to DeepSeek API")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_cognimap_context():
    """Test DeepSeek with CogniMap-specific context"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    print("\n📊 Testing CogniMap Analysis with DeepSeek V3...")
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # CogniMap-specific test
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert software architect analyzing codebases."
            },
            {
                "role": "user",
                "content": """Analyze this component and identify potential architectural issues:
                
Component: UserAuthService
Type: Service
Language: Python
Connections: 5 incoming, 12 outgoing
Semantic Tags: ['authentication', 'security', 'database', 'api']
Metrics: {
    'complexity': 8.5,
    'coupling': 'high',
    'cohesion': 'medium'
}

Provide a brief analysis (2-3 sentences) focusing on the high coupling issue."""
            }
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print("✅ CogniMap analysis successful!")
            print("\n🤖 AI Analysis:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            
            if 'usage' in data:
                print(f"\n📈 Tokens used: {data['usage']['total_tokens']}")
                print(f"   - Prompt: {data['usage']['prompt_tokens']}")
                print(f"   - Completion: {data['usage']['completion_tokens']}")
            
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 DeepSeek V3 API Connection Test")
    print("=" * 60)
    
    # Test basic connection
    success = test_deepseek_v3()
    
    # If basic test passed, test with CogniMap context
    if success:
        test_cognimap_context()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! DeepSeek V3 is ready for CogniMap")
    else:
        print("❌ Connection test failed. Please check your API key and network")
    print("=" * 60)