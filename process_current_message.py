#!/usr/bin/env python3
"""
現在のチャットメッセージをCC-MCPサーバーで処理
"""

import asyncio
import json
from main import CCMCPServer

async def process_current_chat():
    """現在のチャットメッセージを処理"""
    
    print("🎯 現在のチャットメッセージをCC-MCP Serverで処理...")
    print()
    
    server = CCMCPServer()
    
    try:
        # ユーザーの最新メッセージ
        user_message = "このチャットで使用して。"
        session_id = "current-chat-session"
        
        print(f"💬 ユーザーメッセージ: '{user_message}'")
        print()
        
        # CC-MCPサーバーで処理
        result = await server.process_user_message(user_message, session_id)
        
        if "error" in result.get("metadata", {}):
            print(f"❌ エラー: {result['metadata']['error']}")
            return
        
        # 処理結果
        intent = result["metadata"]["intent"]
        keywords = result["metadata"].get("keywords", [])
        ai_response = result["ai_response"]
        context_stats = result["metadata"].get("context_stats", {})
        
        print("📊 === CC-MCP Server 分析結果 ===")
        print()
        print(f"🎯 意図分類: {intent['intent']}")
        print(f"💭 分類理由: {intent['reason']}")
        print()
        
        if keywords:
            print("🔍 抽出キーワード:")
            for kw in keywords[:3]:
                if isinstance(kw, dict):
                    print(f"   - {kw['keyword']} (重要度: {kw['score']:.3f})")
                else:
                    print(f"   - {kw}")
            print()
        
        print("📋 コンテキスト状態:")
        print(f"   - Core Problem: {'✅ 設定済み' if context_stats.get('core_problem') else '❌ 未設定'}")
        print(f"   - Evolving Items: {context_stats.get('evolving_count', 0)}件")
        print(f"   - Recent Messages: {context_stats.get('turn_count', 0)}件")
        print()
        
        print("🤖 CC-MCP Server の応答:")
        print(f"   {ai_response}")
        print()
        
        # 実際のチャット用の応答を生成
        print("💡 === 実際のチャット応答 ===")
        print()
        print("了解しました！今後このチャットでCC-MCPサーバーを使用します。")
        print()
        print("CC-MCPサーバーの分析によると、あなたのメッセージは以下のように解釈されました：")
        print(f"- 意図: {intent['intent'][0] if isinstance(intent['intent'], list) else intent['intent']}")
        print(f"- 内容: {intent['reason']}")
        print()
        print("これからの対話では、CC-MCPサーバーが：")
        print("✅ あなたのメッセージの意図を自動分析")
        print("✅ 重要な制約や決定事項を記憶")
        print("✅ 対話の一貫性を維持")
        print("✅ 適切なコンテキストでAI応答を生成")
        print()
        print("何かご質問や課題がありましたら、お気軽にお聞かせください！")
        print("CC-MCPサーバーが文脈を管理しながら、最適な支援を提供します。")
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await server.close()

if __name__ == "__main__":
    asyncio.run(process_current_chat())
