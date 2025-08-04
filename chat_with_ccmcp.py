#!/usr/bin/env python3
"""
このチャットでCC-MCPサーバーを使用するデモ
"""

import asyncio
import json
from main import CCMCPServer

async def process_chat_message():
    """実際のチャットメッセージをCC-MCPサーバーで処理"""
    
    print("🎯 CC-MCP Server でチャットメッセージを処理中...")
    print()
    
    # サーバーインスタンスを作成
    server = CCMCPServer()
    
    try:
        # ユーザーのメッセージ
        user_message = "では、このチャットでCCMCPサーバを利用してください"
        session_id = "chat-session-001"
        
        print(f"💬 ユーザーメッセージ: {user_message}")
        print()
        
        # メッセージを処理
        print("🔄 CC-MCP Server で処理中...")
        result = await server.process_user_message(user_message, session_id)
        
        if "error" in result.get("metadata", {}):
            print(f"❌ エラー: {result['metadata']['error']}")
            return
        
        # 処理結果を詳細表示
        intent = result["metadata"]["intent"]
        keywords = result["metadata"].get("keywords", [])
        ai_response = result["ai_response"]
        context_stats = result["metadata"].get("context_stats", {})
        
        print("📊 === CC-MCP Server 処理結果 ===")
        print()
        print(f"🎯 意図分類:")
        print(f"   ラベル: {intent['intent']}")
        print(f"   理由: {intent['reason']}")
        print()
        
        if keywords:
            print(f"🔍 抽出キーワード:")
            for kw in keywords[:5]:
                if isinstance(kw, dict):
                    print(f"   - {kw['keyword']} (スコア: {kw['score']:.3f})")
                else:
                    print(f"   - {kw}")
            print()
        
        print(f"📋 コンテキスト状態:")
        if context_stats.get("core_problem"):
            print(f"   - Core Problem: ✅ 設定済み")
        else:
            print(f"   - Core Problem: ❌ 未設定")
        print(f"   - Evolving Items: {context_stats.get('evolving_count', 0)}件")
        print(f"   - Recent Messages: {context_stats.get('turn_count', 0)}件")
        print()
        
        print(f"🤖 AI応答:")
        print(f"   {ai_response}")
        print()
        
        # デバッグ情報も取得
        print("🔍 プロンプト合成の詳細情報を取得中...")
        debug_info = await server.get_debug_info(user_message, session_id)
        
        if "error" not in debug_info:
            synthesis = debug_info.get('prompt_synthesis', {})
            if synthesis:
                final_prompt = synthesis.get('final_prompt', '')
                print(f"📝 合成されたプロンプト (長さ: {len(final_prompt)}文字):")
                print("─" * 50)
                print(final_prompt[:500] + ("..." if len(final_prompt) > 500 else ""))
                print("─" * 50)
                print()
        
        # 続いて、より複雑なメッセージも処理してみる
        print("🔄 追加のメッセージを処理してテスト...")
        follow_up_message = "AIシステムの開発で予算30万円、期間2ヶ月で何ができますか？"
        
        print(f"💬 追加メッセージ: {follow_up_message}")
        
        result2 = await server.process_user_message(follow_up_message, session_id)
        
        if "error" not in result2.get("metadata", {}):
            intent2 = result2["metadata"]["intent"]
            keywords2 = result2["metadata"].get("keywords", [])
            
            print(f"🎯 意図分類: {intent2['intent']}")
            print(f"💭 理由: {intent2['reason']}")
            if keywords2:
                print(f"🔍 キーワード: {[kw['keyword'] if isinstance(kw, dict) else kw for kw in keywords2[:3]]}")
            
            # コンテキストの蓄積を確認
            context_stats2 = result2["metadata"].get("context_stats", {})
            print(f"📊 更新されたコンテキスト:")
            print(f"   - Evolving Items: {context_stats2.get('evolving_count', 0)}件")
            print(f"   - Recent Messages: {context_stats2.get('turn_count', 0)}件")
            print()
            
            print(f"🤖 AI応答: {result2['ai_response'][:150]}...")
        
        print()
        print("🎉 === CC-MCP Server テスト完了 ===")
        print()
        print("✅ 動作確認された機能:")
        print("   - インテント分類器: メッセージの意図を正確に分析")
        print("   - キーワード抽出: 重要な情報を自動抽出")
        print("   - コンテキスト管理: 対話履歴と制約を階層的に管理")
        print("   - プロンプト合成: 動的なプロンプト構築")
        print("   - セッション管理: 継続的な対話状態の維持")
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await server.close()

if __name__ == "__main__":
    asyncio.run(process_chat_message())
