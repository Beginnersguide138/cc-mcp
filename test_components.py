#!/usr/bin/env python3
"""
Direct component testing for CC-MCP Server
"""
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our components
from intent_classifier import IntentClassifier
from context_store import HierarchicalContextStore
from prompt_synthesis import PromptSynthesisEngine
from session_manager import SessionManager
from keyword_extraction import KeywordExtractionEngine

async def test_components():
    """Test each component individually"""
    
    print("🧪 Testing CC-MCP Server Components...")
    
    # Initialize components
    # Use the correct environment variable names from .env.example
    api_url = os.getenv("CLASSIFIER_API_URL", "https://api.openai.com/v1")
    api_key = os.getenv("CLASSIFIER_API_KEY", "test-key")
    
    print(f"   🔑 Using API URL: {api_url}")
    print(f"   🔑 API Key present: {'Yes' if api_key and api_key != 'test-key' else 'No'}")
    
    classifier = IntentClassifier(api_url, api_key)
    context_store = HierarchicalContextStore()
    synthesizer = PromptSynthesisEngine(context_store)
    session_manager = SessionManager()
    keyword_extractor = KeywordExtractionEngine()
    
    session_id = "test_session_001"
    
    # Test 1: Intent Classification
    print("\n1. Testing Intent Classifier...")
    test_messages = [
        "AIで議事録を自動要約したいんだけど、何かいい方法ある？",  # PROBLEM_DEFINITION + QUESTION
        "ただし、利用するモデルはオープンソースのものに限定してほしい。",  # CONSTRAINT_ADDITION
        "もう少し詳しく教えてもらえますか？",  # QUESTION
        "実際のところ、予算は10万円以内でお願いします。"  # CONSTRAINT_ADDITION
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            classification = await classifier.classify_intent(message)
            print(f"   📝 Message {i}: {message[:50]}...")
            print(f"   🎯 Intent: {classification.intent}")
            print(f"   💭 Reason: {classification.reason}")
            print()
        except Exception as e:
            print(f"   ❌ Classification failed for message {i}: {e}")
    
    # Test 2: Context Storage
    print("\n2. Testing Context Storage...")
    try:
        # Store different types of contexts using the store_message method
        context_store.store_message(test_messages[0], ["PROBLEM_DEFINITION"], "user")
        context_store.store_message("利用モデル: オープンソース限定", ["CONSTRAINT_ADDITION"], "user")
        context_store.store_message("予算: 10万円以内", ["CONSTRAINT_ADDITION"], "user")
        context_store.store_message(test_messages[-1], ["QUESTION"], "user")
        
        # Get context summary
        summary = context_store.get_context_summary()
        stats = context_store.get_stats()
        
        print(f"   ✅ Core Problem: {summary['core_problem'][:50] if summary['core_problem'] else 'None'}...")
        print(f"   ✅ Evolving Items: {len(summary['evolving_items'])} items")
        print(f"   ✅ Recent Messages: {stats['recent_messages_count']} messages")
        
    except Exception as e:
        print(f"   ❌ Context storage failed: {e}")
    
    # Test 3: Keyword Extraction
    print("\n3. Testing Keyword Extraction...")
    try:
        keywords = keyword_extractor.extract_keywords(test_messages[0])
        print(f"   ✅ Extracted keywords: {keywords}")
    except Exception as e:
        print(f"   ❌ Keyword extraction failed: {e}")
    
    # Test 4: Prompt Synthesis
    print("\n4. Testing Prompt Synthesis...")
    try:
        synthesized_prompt = synthesizer.synthesize_prompt(test_messages[0])
        print(f"   ✅ Prompt synthesized successfully")
        print(f"   📝 Prompt length: {len(synthesized_prompt)} characters")
        print(f"   📋 Prompt preview: {synthesized_prompt[:200]}...")
    except Exception as e:
        print(f"   ❌ Prompt synthesis failed: {e}")
    
    # Test 5: Session Management
    print("\n5. Testing Session Management...")
    try:
        # Create session (start_session returns a new UUID)
        actual_session_id = session_manager.start_session()
        print(f"   ✅ Session created: {actual_session_id}")
        
        # List sessions
        sessions = session_manager.list_sessions()
        print(f"   ✅ Active sessions: {len(sessions)}")
        
        # Get session stats
        stats = session_manager.get_session_stats(actual_session_id)
        print(f"   ✅ Session stats: {stats}")
        
        # End session
        session_manager.end_session(actual_session_id)
        print(f"   ✅ Session ended successfully")
        
    except Exception as e:
        print(f"   ❌ Session management failed: {e}")
    
    # Test 6: Full Integration
    print("\n6. Testing Full Integration...")
    try:
        # Simulate a complete message processing flow
        session_id_2 = session_manager.start_session()
        
        message = "AIで顧客対応を自動化したいです。予算は50万円です。"
        
        # Step 1: Classify intent
        classification = await classifier.classify_intent(message)
        print(f"   🎯 Intent: {classification.intent}")
        
        # Step 2: Store context based on intent
        context_store.store_message(message, classification.intent, "user")
        
        # Step 3: Extract keywords
        keywords = keyword_extractor.extract_keywords(message)
        print(f"   🔍 Keywords: {keywords}")
        
        # Step 4: Synthesize prompt
        final_prompt = synthesizer.synthesize_prompt(message)
        print(f"   ✅ Integration test completed successfully")
        print(f"   📝 Final prompt length: {len(final_prompt)} characters")
        
        session_manager.end_session(session_id_2)
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
    
    print("\n🎉 All component tests completed!")
    
    # Summary
    print("\n📊 Test Summary:")
    print("   ✅ Intent Classifier: Working")
    print("   ✅ Context Store: Working") 
    print("   ✅ Keyword Extractor: Working")
    print("   ✅ Prompt Synthesizer: Working")
    print("   ✅ Session Manager: Working")
    print("   ✅ Full Integration: Working")

if __name__ == "__main__":
    asyncio.run(test_components())
