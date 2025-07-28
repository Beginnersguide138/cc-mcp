import asyncio
import json
from dotenv import load_dotenv
from intent_classifier import IntentClassifier

load_dotenv()

async def test_classifier_with_debug():
    """Test classifier with detailed debug output"""
    
    import os
    
    classifier = IntentClassifier(
        api_url=os.getenv("CLASSIFIER_API_URL"),
        api_key=os.getenv("CLASSIFIER_API_KEY"),
        model=os.getenv("CLASSIFIER_MODEL")
    )
    
    try:
        print("🧪 Testing intent classification...")
        
        # Override the classify_intent method to see what's happening
        prompt = classifier.PROMPT_TEMPLATE.format(user_message="AIで議事録を自動要約したいです")
        
        print("📝 Prompt being sent:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_completion_tokens": 200
        }
        
        headers = {
            "api-key": os.getenv("CLASSIFIER_API_KEY"),
            "Content-Type": "application/json"
        }
        
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("CLASSIFIER_API_URL"),
                json=payload,
                headers=headers
            )
            
            print(f"✅ Status: {response.status_code}")
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            print("📄 Raw LLM Response:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print(f"✅ Successfully parsed JSON: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print("🔧 Will use fallback UNCLEAR classification")
                
        # Now test the actual classifier method
        print("\n🧪 Testing actual classifier method...")
        result = await classifier.classify_intent("AIで議事録を自動要約したいです")
        print(f"✅ Classifier result: {result}")
        
    finally:
        await classifier.close()

if __name__ == "__main__":
    asyncio.run(test_classifier_with_debug())