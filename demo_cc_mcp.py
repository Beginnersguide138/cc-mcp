#!/usr/bin/env python3
"""
CC-MCP実機能デモンストレーション
ユーザーの質問「CC-MCPには、どんな機能がありますか？また、その仕組についても教えて下さい。」
を実際にCC-MCPシステムで処理
"""

import asyncio
import json
from dotenv import load_dotenv
import os

# 環境変数読み込み
load_dotenv()

async def demo_cc_mcp_functionality():
    """CC-MCPの機能をデモンストレーション"""
    
    print("🚀 CC-MCP実機能デモンストレーション")
    print("=" * 60)
    print("質問: 「CC-MCPには、どんな機能がありますか？また、その仕組についても教えて下さい。」")
    print("=" * 60)
    
    # Step 1: コンポーネントのインポート
    from intent_classifier import IntentClassifier
    from context_store import HierarchicalContextStore  
    from prompt_synthesis import PromptSynthesisEngine
    
    # Step 2: CC-MCPシステム初期化
    print("\n📋 Step 1: CC-MCPシステム初期化")
    
    classifier = IntentClassifier(
        api_url=os.getenv("CLASSIFIER_API_URL"),
        api_key=os.getenv("CLASSIFIER_API_KEY"),
        model=os.getenv("CLASSIFIER_MODEL")
    )
    
    context_store = HierarchicalContextStore()
    prompt_engine = PromptSynthesisEngine(context_store)
    
    print("✅ インテント分類器初期化完了")
    print("✅ 階層型コンテキストストア初期化完了") 
    print("✅ プロンプト合成エンジン初期化完了")
    
    # Step 3: ユーザーメッセージのインテント分析
    user_message = "CC-MCPには、どんな機能がありますか？また、その仕組についても教えて下さい。"
    
    print(f"\n📋 Step 2: インテント分析")
    print(f"入力メッセージ: {user_message}")
    
    intent_result = await classifier.classify_intent(user_message)
    
    print(f"✅ 分析結果:")
    print(f"   インテント: {intent_result.intent}")
    print(f"   理由: {intent_result.reason}")
    
    # Step 4: コンテキストストアに保存
    print(f"\n📋 Step 3: コンテキスト管理")
    
    context_store.store_message(
        content=user_message,
        intent_labels=intent_result.intent,
        role="user"
    )
    
    # コンテキスト状況を表示
    context_summary = context_store.get_context_summary()
    print(f"✅ コンテキスト保存完了:")
    print(f"   Core Context (問題定義): {context_summary['core_problem'] is not None}")
    print(f"   Evolving Context (制約等): {len(context_summary['evolving_items'])} 項目")
    print(f"   Turn Context (会話履歴): 保存済み")
    
    # Step 5: プロンプト合成
    print(f"\n📋 Step 4: インテリジェント・プロンプト合成")
    
    synthesized_prompt = prompt_engine.synthesize_prompt(user_message)
    
    print("✅ プロンプト合成完了:")
    print("--- 合成されたプロンプト (抜粋) ---")
    prompt_lines = synthesized_prompt.split('\n')
    for i, line in enumerate(prompt_lines[:15]):  # 最初の15行のみ表示
        print(f"   {line}")
    if len(prompt_lines) > 15:
        print(f"   ... (残り{len(prompt_lines)-15}行)")
    print("--- プロンプト終了 ---")
    
    # Step 6: メインLLMでの応答生成
    print(f"\n📋 Step 5: メインLLM応答生成")
    
    import httpx
    
    payload = {
        "model": os.getenv("MAIN_MODEL", "gpt-4"),
        "messages": [
            {"role": "user", "content": synthesized_prompt}
        ],
        "max_tokens": 1000,
        "temperature": float(os.getenv("MAIN_TEMPERATURE", "0.7"))
    }
    
    headers = {
        "Authorization": f"Bearer {os.getenv('MAIN_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            os.getenv("MAIN_API_URL"),
            json=payload,
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            
            print("✅ LLM応答生成完了:")
            print("--- CC-MCPからの回答 ---")
            print(ai_response)
            print("--- 回答終了 ---")
            
            # Step 7: 応答をコンテキストに保存
            print(f"\n📋 Step 6: 応答のコンテキスト保存")
            
            context_store.store_message(
                content=ai_response,
                intent_labels=["RESPONSE"],
                role="assistant"  
            )
            
            print("✅ 応答がコンテキストに保存されました")
            
        else:
            print(f"❌ LLM API エラー: {response.status_code}")
            print(f"詳細: {response.text}")
    
    # Step 8: システム状態の確認
    print(f"\n📋 Step 7: システム状態確認")
    
    final_summary = context_store.get_context_summary()
    print("✅ 最終コンテキスト状況:")
    print(f"   Core Context: {final_summary['core_problem'] is not None}")
    print(f"   Evolving Context: {len(final_summary['evolving_items'])} 項目")
    print(f"   Turn Context (会話): 2ターン保存済み")
    
    # エクスポート機能のデモ
    exported_context = context_store.export_state()
    print(f"   エクスポート可能サイズ: {len(exported_context)} 文字")
    
    await classifier.close()
    
    print(f"\n🎉 CC-MCP機能デモンストレーション完了!")
    print("📋 このようにCC-MCPは、ユーザーの質問を階層的に管理し、")
    print("   長期的な対話一貫性を維持しながら応答を生成します。")

if __name__ == "__main__":
    asyncio.run(demo_cc_mcp_functionality())
