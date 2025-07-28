import asyncio
import json
from unittest.mock import AsyncMock, patch
from main import MCPServer


async def test_basic_functionality():
    """Test basic MCP server functionality with mocked LLM calls"""
    
    # Create server instance
    server = MCPServer()
    
    # Mock the LLM API calls to avoid actual API requests
    with patch.object(server.intent_classifier, 'classify_intent') as mock_classifier, \
         patch.object(server, '_call_main_llm') as mock_main_llm:
        
        # Setup mocks
        mock_classifier.return_value = AsyncMock()
        mock_classifier.return_value.intent = ["PROBLEM_DEFINITION"]
        mock_classifier.return_value.reason = "ユーザーが問題を定義している"
        
        mock_main_llm.return_value = "こんにちは！お手伝いさせていただきます。"
        
        # Test 1: Process a problem definition message
        print("🧪 Testing problem definition message...")
        result = await server.process_message("AIで議事録を自動要約したいです")
        
        print(f"✅ Response: {result['response']}")
        print(f"✅ Intent: {result['metadata']['intent_classification']['intent']}")
        print(f"✅ Reason: {result['metadata']['intent_classification']['reason']}")
        
        # Test 2: Add a constraint
        mock_classifier.return_value.intent = ["CONSTRAINT_ADDITION"]
        mock_classifier.return_value.reason = "制約を追加している"
        mock_main_llm.return_value = "オープンソースのモデルに限定しますね。"
        
        print("\n🧪 Testing constraint addition...")
        result = await server.process_message("オープンソースのモデルに限定してください")
        
        print(f"✅ Response: {result['response']}")
        print(f"✅ Intent: {result['metadata']['intent_classification']['intent']}")
        
        # Test 3: Check context stats
        print("\n🧪 Testing context stats...")
        stats = server.prompt_engine.get_context_stats()
        print(f"✅ Has core problem: {stats['has_core_problem']}")
        print(f"✅ Evolving items count: {stats['evolving_items_count']}")
        print(f"✅ Recent messages count: {stats['recent_messages_count']}")
        
        # Test 4: Export context
        print("\n🧪 Testing context export...")
        exported = await server.get_context_export()
        context_data = json.loads(exported)
        print(f"✅ Exported context keys: {list(context_data.keys())}")
        
        # Test 5: Clear context
        print("\n🧪 Testing context clear...")
        cleared = await server.clear_context()
        print(f"✅ Context cleared: {cleared}")
        
        stats_after_clear = server.prompt_engine.get_context_stats()
        print(f"✅ Has core problem after clear: {stats_after_clear['has_core_problem']}")
        
    await server.close()
    print("\n✨ All tests completed successfully!")


async def test_prompt_synthesis():
    """Test prompt synthesis with actual context data"""
    
    print("\n🧪 Testing prompt synthesis...")
    
    # Create components
    from context_store import HierarchicalContextStore, Message
    from prompt_synthesis import PromptSynthesisEngine
    
    context_store = HierarchicalContextStore()
    prompt_engine = PromptSynthesisEngine(context_store)
    
    # Add some test data
    context_store.store_message(
        "AIで議事録を自動要約したい",
        ["PROBLEM_DEFINITION"],
        "user"
    )
    
    context_store.store_message(
        "オープンソースモデルに限定",
        ["CONSTRAINT_ADDITION"],
        "user"
    )
    
    context_store.store_message(
        "承知しました。オープンソースのモデルを使って議事録要約システムを提案します。",
        ["RESPONSE"],
        "assistant"
    )
    
    # Test prompt synthesis
    current_message = "具体的にはどのモデルがおすすめですか？"
    synthesized = prompt_engine.synthesize_prompt(current_message)
    
    print("✅ Synthesized prompt:")
    print("-" * 50)
    print(synthesized)
    print("-" * 50)
    
    # Test debug info
    debug_info = prompt_engine.create_debug_info(current_message)
    print(f"✅ Debug info keys: {list(debug_info.keys())}")
    print(f"✅ Prompt length: {debug_info['output']['prompt_length']}")


def run_tests():
    """Run all tests"""
    print("🚀 Starting CC-MCP Server Tests...\n")
    
    async def run_all():
        await test_basic_functionality()
        await test_prompt_synthesis()
    
    asyncio.run(run_all())


if __name__ == "__main__":
    run_tests()