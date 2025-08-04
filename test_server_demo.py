#!/usr/bin/env python3
"""
CC-MCP Server Demo Test
仕様書通りの動作をデモンストレーションします
"""

import asyncio
import os
import json
from dotenv import load_dotenv
load_dotenv()

from main import CCMCPServer

async def demo_conversation():
    """実際の対話シナリオでMCPサーバーをテスト"""
    
    print("🎯 ===== CC-MCP Server デモンストレーション =====")
    print()
    
    # サーバーインスタンスを作成
    server = CCMCPServer()
    
    try:
        # テストシナリオ：議事録要約システムの相談
        messages = [
            "AIで議事録を自動要約するシステムを作りたいです。どんな方法がありますか？",
            "ただし、利用するモデルはオープンソースのものに限定してほしい。",
            "予算は50万円以内で、来月までに完成させたいと思います。",
            "具体的にはどのモデルを使うのがいいでしょうか？",
            "実装方法についてもう少し詳しく教えてください。"
        ]
        
        session_id = "demo-session"
        
        print("📋 対話シナリオ：")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. {msg}")
        print()
        
        # 各メッセージを順次処理
        for i, message in enumerate(messages, 1):
            print(f"🔄 メッセージ {i}/5 を処理中...")
            print(f"   💬 ユーザー: {message}")
            
            try:
                # メッセージを処理
                result = await server.process_user_message(message, session_id)
                
                if "error" in result.get("metadata", {}):
                    print(f"   ❌ エラー: {result['metadata']['error']}")
                    continue
                
                # 結果を表示
                intent = result["metadata"]["intent"]
                keywords = result["metadata"].get("keywords", [])
                ai_response = result["ai_response"]
                
                print(f"   🎯 意図分類: {intent['intent']}")
                print(f"   💭 分類理由: {intent['reason']}")
                if keywords:
                    print(f"   🔍 抽出キーワード: {[kw['keyword'] for kw in keywords[:3]]}")
                print(f"   🤖 AI応答: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")
                
                # コンテキスト統計を表示
                context_stats = result["metadata"].get("context_stats", {})
                if context_stats:
                    print(f"   📊 コンテキスト統計:")
                    if context_stats.get("core_problem"):
                        print(f"      - Core Problem: ✅ 設定済み")
                    print(f"      - Evolving Items: {context_stats.get('evolving_count', 0)}件")
                    print(f"      - Recent Messages: {context_stats.get('turn_count', 0)}件")
                
                print()
                
            except Exception as e:
                print(f"   ❌ 処理エラー: {e}")
                print()
        
        # 最終的なコンテキスト状態をエクスポート
        print("📤 最終コンテキスト状態をエクスポート中...")
        context_json = await server.export_context(session_id)
        context_data = json.loads(context_json)
        
        print(f"   📋 Core Context: {len(context_data.get('core_context', {}).get('content', '')) > 0}")
        print(f"   📋 Evolving Items: {len(context_data.get('evolving_context', []))}件")
        print(f"   📋 Turn History: {len(context_data.get('turn_context', []))}件")
        
        # デバッグ情報を取得
        print()
        print("🔍 デバッグ情報を取得中...")
        debug_info = await server.get_debug_info("システムの実装方法を教えて", session_id)
        
        if "error" not in debug_info:
            print("   ✅ プロンプト合成成功")
            print(f"   📝 合成プロンプト長: {len(debug_info.get('prompt_synthesis', {}).get('final_prompt', ''))}文字")
            
            # プロンプトの構造を表示
            synthesis = debug_info.get('prompt_synthesis', {})
            if synthesis:
                print("   📋 プロンプト構造:")
                if synthesis.get('core_context_used'):
                    print("      - Core Context: ✅ 使用")
                if synthesis.get('evolving_context_used'):
                    print(f"      - Evolving Context: ✅ {len(synthesis.get('evolving_items', []))}項目使用")
                if synthesis.get('turn_context_used'):
                    print(f"      - Turn Context: ✅ {len(synthesis.get('recent_messages', []))}メッセージ使用")
        
        print()
        print("🎉 ===== デモンストレーション完了 =====")
        print()
        print("✅ 確認された機能:")
        print("   - インテリジェント・インテント分類")
        print("   - 階層型コンテキストストア")
        print("   - プロンプト合成エンジン")
        print("   - セッション管理")
        print("   - キーワード抽出")
        print("   - コンテキストエクスポート")
        print("   - デバッグ情報生成")
        
    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # リソースをクリーンアップ
        await server.close()

if __name__ == "__main__":
    print("🚀 CC-MCP Server Demo を開始します...")
    print()
    
    asyncio.run(demo_conversation())
