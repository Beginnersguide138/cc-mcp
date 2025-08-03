#!/usr/bin/env python3
"""
CC-MCP Live Functionality Test
長期対話一貫性のリアルタイムテスト
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from intent_classifier import IntentClassifier
from context_store import HierarchicalContextStore
from prompt_synthesis import PromptSynthesisEngine
import httpx

class CCMCPLiveTest:
    def __init__(self):
        # Initialize components
        self.context_store = HierarchicalContextStore()
        self.prompt_engine = PromptSynthesisEngine(self.context_store)
        
        classifier_api_url = os.getenv("CLASSIFIER_API_URL", "https://api.openai.com/v1/chat/completions")
        classifier_api_key = os.getenv("CLASSIFIER_API_KEY", "")
        classifier_model = os.getenv("CLASSIFIER_MODEL", "gpt-3.5-turbo")
        
        self.intent_classifier = IntentClassifier(
            api_url=classifier_api_url,
            api_key=classifier_api_key,
            model=classifier_model
        )
        
        # Main LLM configuration
        self.main_api_url = os.getenv("MAIN_API_URL", "https://api.openai.com/v1/chat/completions")
        self.main_api_key = os.getenv("MAIN_API_KEY", "")
        self.main_model = os.getenv("MAIN_MODEL", "gpt-4")
        self.main_temperature = float(os.getenv("MAIN_TEMPERATURE", "0.7"))
        
        self.http_client = httpx.AsyncClient()
    
    async def process_message(self, user_message: str, session_id: str = "default"):
        """Process a user message through the complete MCP pipeline."""
        try:
            print(f"🔄 Processing: {user_message}")
            
            # Step 1: Classify intent
            intent_result = await self.intent_classifier.classify_intent(user_message)
            print(f"📊 Intent: {intent_result.intent} - {intent_result.reason}")
            
            # Step 2: Store in context based on intent
            self.context_store.store_message(
                content=user_message,
                intent_labels=intent_result.intent,
                role="user"
            )
            
            # Step 3: Synthesize prompt with context
            synthesized_prompt = self.prompt_engine.synthesize_prompt(user_message)
            
            # Step 4: Generate response from main LLM
            main_response = await self._call_main_llm(synthesized_prompt)
            
            # Step 5: Store assistant response in turn context
            self.context_store.store_message(
                content=main_response,
                intent_labels=["RESPONSE"],
                role="assistant"
            )
            
            print(f"💬 Response: {main_response[:200]}...")
            print(f"📈 Context Stats: {self.prompt_engine.get_context_stats()}")
            print("-" * 60)
            
            return {
                "response": main_response,
                "metadata": {
                    "intent_classification": {
                        "intent": intent_result.intent,
                        "reason": intent_result.reason
                    },
                    "context_stats": self.prompt_engine.get_context_stats(),
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                "response": "申し訳ございませんが、処理中にエラーが発生しました。",
                "metadata": {"error": str(e), "session_id": session_id}
            }
    
    async def _call_main_llm(self, prompt: str) -> str:
        """Call the main LLM with the synthesized prompt"""
        payload = {
            "model": self.main_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": self.main_temperature
        }
        
        headers = {
            "Authorization": f"Bearer {self.main_api_key}",
            "Content-Type": "application/json"
        }
        
        response = await self.http_client.post(
            self.main_api_url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    async def close(self):
        """Clean up resources"""
        await self.intent_classifier.close()
        await self.http_client.aclose()

async def main():
    """Interactive CC-MCP test session"""
    print("🚀 CC-MCP Live Functionality Test")
    print("=" * 60)
    print("長期対話一貫性のテストを開始します...")
    print()
    
    test_system = CCMCPLiveTest()
    
    # Test scenario: 段階的な要求の発展
    test_messages = [
        "Webアプリの開発プロジェクトを始めたいです。Vue.jsを使いたいと思います。",
        "ただし、予算は10万円以内で、期間は2ヶ月以内でお願いします。",
        "実は、ユーザー認証機能も必要です。セキュリティを重視してください。",
        "最初の質問に戻りますが、どのような技術スタックがおすすめですか？"
    ]
    
    try:
        for i, message in enumerate(test_messages, 1):
            print(f"🔷 ターン {i}: 対話一貫性テスト")
            await test_system.process_message(message, "live_test_session")
            print()
            
            # Show evolving context
            stats = test_system.prompt_engine.get_context_stats()
            print(f"📋 現在のコンテキスト状況:")
            print(f"   Core Context: {'設定済み' if stats['has_core_problem'] else '未設定'}")
            print(f"   Evolving Context: {stats['evolving_items_count']} 項目")
            print(f"   Turn Context: {stats['recent_messages_count']} メッセージ")
            print()
            
            if i < len(test_messages):
                input("⏳ 次のターンに進むには Enter を押してください...")
                print()
    
    finally:
        await test_system.close()
        print("🏁 テスト完了")

if __name__ == "__main__":
    asyncio.run(main())
