#!/usr/bin/env python3
"""
OpenAI APIキーの詳細テストと診断
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv()

async def test_api_key_detailed():
    """APIキーの詳細テストと診断"""
    
    print("🔍 OpenAI APIキー詳細診断")
    print("=" * 50)
    
    api_key = os.getenv("CLASSIFIER_API_KEY")
    api_url = os.getenv("CLASSIFIER_API_URL")
    
    print(f"📋 設定確認:")
    print(f"   API URL: {api_url}")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    print(f"   Model: {os.getenv('CLASSIFIER_MODEL')}")
    
    if not api_key:
        print("❌ APIキーが設定されていません")
        return
    
    # Test 1: 最小限のリクエスト
    print(f"\n🧪 テスト1: 最小限のリクエスト")
    
    minimal_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 10
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("   リクエスト送信中...")
            response = await client.post(
                api_url,
                json=minimal_payload,
                headers=headers,
                timeout=10.0
            )
            
            print(f"   ステータス: {response.status_code}")
            print(f"   レスポンス: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ 最小限のリクエスト成功")
            else:
                print("❌ 最小限のリクエスト失敗")
                
        except Exception as e:
            print(f"❌ リクエストエラー: {str(e)}")
    
    # Test 2: モデル一覧取得
    print(f"\n🧪 テスト2: 利用可能なモデル確認")
    
    models_url = "https://api.openai.com/v1/models"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                models_url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            
            print(f"   ステータス: {response.status_code}")
            
            if response.status_code == 200:
                models_data = response.json()
                model_ids = [model["id"] for model in models_data.get("data", [])]
                available_models = [m for m in model_ids if "gpt" in m][:5]
                print(f"✅ 利用可能なGPTモデル: {available_models}")
            else:
                print(f"❌ モデル一覧取得失敗: {response.text}")
                
        except Exception as e:
            print(f"❌ モデル一覧エラー: {str(e)}")
    
    # Test 3: 異なるモデルでのテスト
    print(f"\n🧪 テスト3: 異なるモデルでのテスト")
    
    test_models = ["gpt-3.5-turbo", "gpt-4o-mini"]
    
    for model in test_models:
        print(f"   テストモデル: {model}")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 5
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"   ✅ {model}: 成功")
                else:
                    print(f"   ❌ {model}: 失敗 ({response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {model}: エラー ({str(e)})")
    
    # Test 4: 組織情報の確認
    print(f"\n🧪 テスト4: 組織情報確認")
    
    org_url = "https://api.openai.com/v1/organizations"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                org_url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            
            print(f"   ステータス: {response.status_code}")
            
            if response.status_code == 200:
                org_data = response.json()
                print(f"✅ 組織情報取得成功")
                # 組織情報を表示（機密情報は除く）
                if "data" in org_data and org_data["data"]:
                    for org in org_data["data"]:
                        org_id = org.get("id", "N/A")
                        org_name = org.get("name", "N/A")
                        print(f"   組織: {org_name} (ID: {org_id})")
            else:
                print(f"❌ 組織情報取得失敗: {response.text}")
                
        except Exception as e:
            print(f"❌ 組織情報エラー: {str(e)}")
    
    print(f"\n📋 診断完了")
    print("🔧 解決策の提案:")
    print("   1. APIキーが正しく設定されているか確認")
    print("   2. OpenAI組織でのAPIキーの権限を確認")  
    print("   3. 必要に応じて新しいAPIキーを生成")
    print("   4. 代替LLMプロバイダーの利用を検討")

if __name__ == "__main__":
    asyncio.run(test_api_key_detailed())
