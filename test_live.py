import asyncio
import json
from dotenv import load_dotenv
from main import MCPServer

load_dotenv()

async def test_with_real_api():
    """Test the MCP server with real Azure OpenAI API"""
    
    print("🚀 Testing CC-MCP Server with real Azure OpenAI API...\n")
    
    server = MCPServer()
    
    try:
        # Test 1: Problem definition
        print("🧪 Test 1: Problem definition")
        result1 = await server.process_message("AIで議事録を自動要約するシステムを作りたいです")
        print(f"✅ Response: {result1['response']}")
        print(f"✅ Intent: {result1['metadata']['intent_classification']['intent']}")
        print(f"✅ Reason: {result1['metadata']['intent_classification']['reason']}")
        
        # Test 2: Add constraint
        print("\n🧪 Test 2: Add constraint")
        result2 = await server.process_message("ただし、オープンソースのモデルのみを使用してください")
        print(f"✅ Response: {result2['response']}")
        print(f"✅ Intent: {result2['metadata']['intent_classification']['intent']}")
        
        # Test 3: Refinement
        print("\n🧪 Test 3: Refinement")
        result3 = await server.process_message("また、日本語の会議に特化した機能も含めてください")
        print(f"✅ Response: {result3['response']}")
        print(f"✅ Intent: {result3['metadata']['intent_classification']['intent']}")
        
        # Test 4: Question
        print("\n🧪 Test 4: Question")
        result4 = await server.process_message("具体的にはどのようなモデルを推奨しますか？")
        print(f"✅ Response: {result4['response']}")
        print(f"✅ Intent: {result4['metadata']['intent_classification']['intent']}")
        
        # Show context stats
        print("\n📊 Context Statistics:")
        stats = server.prompt_engine.get_context_stats()
        print(f"✅ Has core problem: {stats['has_core_problem']}")
        print(f"✅ Evolving items count: {stats['evolving_items_count']}")
        print(f"✅ Recent messages count: {stats['recent_messages_count']}")
        
        # Show synthesized prompt for the last message
        print("\n🔍 Final synthesized prompt:")
        print("-" * 60)
        final_prompt = server.prompt_engine.synthesize_prompt("どのような技術スタックを推奨しますか？")
        print(final_prompt)
        print("-" * 60)
        
        # Export context
        print("\n💾 Exported context:")
        exported = await server.get_context_export()
        context_data = json.loads(exported)
        print(f"✅ Core problem: {context_data.get('core', {}).get('problem_definition', {}).get('content', 'None')}")
        print(f"✅ Constraints count: {len(context_data.get('evolving', {}).get('constraints', []))}")
        print(f"✅ Refinements count: {len(context_data.get('evolving', {}).get('refinements', []))}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await server.close()
        print("\n✨ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_with_real_api())