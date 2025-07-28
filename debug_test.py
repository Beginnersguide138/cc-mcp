import asyncio
import json
from dotenv import load_dotenv
from intent_classifier import IntentClassifier

load_dotenv()

async def debug_classifier():
    """Debug the intent classifier directly"""
    
    print("🔍 Debugging Intent Classifier...")
    
    import os
    
    api_url = os.getenv("CLASSIFIER_API_URL")
    api_key = os.getenv("CLASSIFIER_API_KEY") 
    model = os.getenv("CLASSIFIER_MODEL")
    
    print(f"API URL: {api_url}")
    print(f"Model: {model}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    
    classifier = IntentClassifier(
        api_url=api_url,
        api_key=api_key,
        model=model
    )
    
    try:
        print("\n🧪 Testing raw API call...")
        
        # Test raw API call first
        import httpx
        
        payload = {
            "messages": [
                {"role": "user", "content": "Hello, test message"}
            ],
            "max_completion_tokens": 200
        }
        
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, headers=headers)
            print(f"✅ HTTP Status: {response.status_code}")
            print(f"✅ Raw Response: {response.text}")
            
            if response.status_code == 200:
                result_json = response.json()
                print(f"✅ Parsed JSON: {json.dumps(result_json, indent=2, ensure_ascii=False)}")
        
        print("\n🧪 Testing classifier with simple message...")
        result = await classifier.classify_intent("AIで議事録を自動要約したいです")
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        
        # Try to get more details from HTTP error
        if hasattr(e, 'response'):
            print(f"❌ HTTP Status: {e.response.status_code}")
            print(f"❌ HTTP Response: {e.response.text}")
    
    finally:
        await classifier.close()

if __name__ == "__main__":
    asyncio.run(debug_classifier())