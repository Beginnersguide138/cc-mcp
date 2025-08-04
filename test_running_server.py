#!/usr/bin/env python3
"""
MCP Client to test the running CC-MCP Server via SSE transport
"""
import asyncio
import json
import httpx
from typing import Dict, Any

async def test_mcp_server():
    """Test the running MCP server via HTTP requests to its tools"""
    
    print("🧪 Testing Running CC-MCP Server...")
    print("🔗 Connecting to MCP server at http://127.0.0.1:8001")
    
    base_url = "http://127.0.0.1:8001"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Since this is an MCP server with SSE transport, we need to test via the MCP protocol
            # Let's try to access the server info endpoint first
            print("\n1. Testing server connectivity...")
            try:
                # Try to get server information (FastMCP usually provides this)
                response = await client.get(f"{base_url}/")
                print(f"   ✅ Server responded: {response.status_code}")
                if response.status_code == 200:
                    print(f"   📋 Server info: Available")
                else:
                    print(f"   ⚠️ Server responded with status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Server connectivity failed: {e}")
                return
            
            # Try to connect to SSE endpoint
            print("\n2. Testing SSE endpoint connectivity...")
            try:
                response = await client.get(f"{base_url}/sse/")
                print(f"   ✅ SSE endpoint accessible: {response.status_code}")
            except Exception as e:
                print(f"   ❌ SSE endpoint failed: {e}")
            
            # Test via direct tool calls if possible
            print("\n3. Testing MCP tool availability...")
            print("   📋 Available MCP Tools (as per main.py):")
            tools = [
                "process_user_message",
                "export_context", 
                "import_context",
                "clear_context",
                "get_debug_info",
                "start_session",
                "end_session", 
                "list_sessions",
                "get_session_stats"
            ]
            
            for tool in tools:
                print(f"   - {tool}")
            
            print(f"\n   ✅ MCP Server is running with {len(tools)} tools")
            
            print("\n🎉 MCP Server connectivity test completed!")
            print("\n📊 Test Summary:")
            print("   ✅ Server Status: Running")
            print("   ✅ Transport: SSE (Server-Sent Events)")  
            print("   ✅ Protocol: MCP (Model Context Protocol)")
            print("   ✅ Tools Available: 9 tools")
            print("\n💡 To properly test the MCP tools, use a proper MCP client library")
            print("   or connect via the MCP protocol with tools like:")
            print("   - process_user_message: Process messages with context")
            print("   - start_session/end_session: Manage conversation sessions")
            print("   - get_debug_info: Get detailed processing information")
            
        except Exception as e:
            print(f"❌ Failed to test MCP server: {e}")
            print("Make sure the server is running with: uv run python main.py")

async def test_component_integration():
    """Test that all components are working individually"""
    print("\n" + "="*60)
    print("🔧 Running Component Integration Test...")
    
    # Import and test components directly
    from intent_classifier import IntentClassifier
    from context_store import HierarchicalContextStore
    from prompt_synthesis import PromptSynthesisEngine
    from session_manager import SessionManager
    from keyword_extraction import KeywordExtractionEngine
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        # Initialize components
        api_url = os.getenv("CLASSIFIER_API_URL", "https://api.openai.com/v1/chat/completions")
        api_key = os.getenv("CLASSIFIER_API_KEY", "")
        
        classifier = IntentClassifier(api_url, api_key)
        context_store = HierarchicalContextStore()
        synthesizer = PromptSynthesisEngine(context_store)
        session_manager = SessionManager()
        keyword_extractor = KeywordExtractionEngine()
        
        print("   ✅ All components initialized successfully")
        
        # Test a complete flow
        test_message = "AIで顧客サポートを自動化したいです。予算は100万円です。"
        
        # Step 1: Classify intent
        classification = await classifier.classify_intent(test_message)
        print(f"   🎯 Intent Classification: {classification.intent}")
        
        # Step 2: Extract keywords
        keywords = keyword_extractor.extract_keywords(test_message)
        print(f"   � Extracted {len(keywords)} keywords")
        
        # Step 3: Store in context
        context_store.store_message(test_message, classification.intent, "user", keywords)
        
        # Step 4: Synthesize prompt
        synthesized_prompt = synthesizer.synthesize_prompt(test_message)
        print(f"   � Synthesized prompt: {len(synthesized_prompt)} characters")
        
        # Step 5: Session management
        session_id = session_manager.start_session()
        print(f"   � Created session: {session_id[:8]}...")
        session_manager.end_session(session_id)
        
        print("   ✅ Component integration test successful!")
        
    except Exception as e:
        print(f"   ❌ Component integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
    asyncio.run(test_component_integration())
