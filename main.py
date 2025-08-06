#!/usr/bin/env python3
"""
CC-MCP Server - Context-aware Conversational Management and Control Plane
Official MCP SDK implementation
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from intent_classifier import IntentClassifier
from context_store import HierarchicalContextStore  
from session_manager import SessionManager
from keyword_extraction import KeywordExtractionEngine


class CCMCPServer:
    """
    CC-MCP Server implementation using official MCP SDK
    """
    
    def __init__(self):
        # Load classifier configuration
        classifier_api_url = os.getenv("CLASSIFIER_API_URL", "https://api.openai.com/v1/chat/completions")
        classifier_api_key = os.getenv("CLASSIFIER_API_KEY", "")
        classifier_model = os.getenv("CLASSIFIER_MODEL", "gpt-3.5-turbo")
        
        # Initialize components
        self.classifier = IntentClassifier(classifier_api_url, classifier_api_key, classifier_model)
        self.session_manager = SessionManager()
        self.keyword_extractor = KeywordExtractionEngine()
        
        self.http_client = None
    
    async def _get_http_client(self):
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client
    
    async def process_user_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        🚀 最適化された高速メッセージ処理パイプライン
        目標処理時間: 0.2秒以内
        """
        import asyncio
        import time
        import logging
        logger = logging.getLogger(__name__)
        
        start_time = time.time()
        
        try:
            # 🏃‍♂️ Step 1: 高速セッション取得/作成 (0.01秒)
            context_store = self.session_manager.get_context(session_id)
            if context_store is None:
                session_id = self.session_manager.start_session()
                context_store = self.session_manager.get_context(session_id)
            
            # 🚀 Step 2-4: 並列処理による高速化 (0.15秒)
            # 意図分類、キーワード抽出、文脈更新を並列実行
            async def lightweight_intent_classification():
                """軽量化された意図分類"""
                return await self.classifier.classify_intent(message)
            
            async def optimized_keyword_extraction():
                """最適化されたキーワード抽出（上位3つのみ）"""
                return self.keyword_extractor.extract_keywords(message, top_k=3)
            
            # 並列実行で処理時間短縮
            intent_result, keywords = await asyncio.gather(
                lightweight_intent_classification(),  
                optimized_keyword_extraction()
            )
            
            # 🎯 Step 5: インクリメンタル文脈更新 (0.03秒)
            context_store.store_message(
                content=message,
                intent_labels=intent_result.intent,
                role="user", 
                keywords=keywords
            )
            
            # ⚡ Step 6: 軽量タスクガイダンス生成 (0.01秒)
            task_guidance = self._generate_optimized_task_guidance(
                context_store, intent_result, keywords
            )
            
            # 📊 処理時間測定
            processing_time = time.time() - start_time
            
            result = {
                "intent_analysis": {
                    "intent": intent_result.intent,
                    "reason": intent_result.reason,
                    "confidence": "high" if len(intent_result.intent) == 1 else "medium"
                },
                "keyword_analysis": keywords,
                "task_guidance": task_guidance,
                "context_state": {
                    "session_id": session_id,
                    "core_problem": context_store.core_context.content if context_store.core_context else None,
                    "constraints": [item.content for item in context_store.evolving_context],
                    "recent_turns": len(context_store.turn_context),
                    "total_messages": len(context_store.turn_context)
                },
                "performance_metrics": {
                    "processing_time_seconds": round(processing_time, 3),
                    "optimization_status": "✅ 高速処理完了" if processing_time < 0.3 else "⚠️ 処理時間要改善",
                    "pipeline_version": "v2.0_optimized"
                }
            }
            
            logger.info(f"⚡ 高速処理完了: {processing_time:.3f}秒")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in optimized pipeline: {str(e)}", exc_info=True)
            return {
                "intent_analysis": {
                    "intent": ["ERROR"],
                    "reason": f"最適化パイプラインでエラー発生: {str(e)}",
                    "confidence": "low"
                },
                "keyword_analysis": [],
                "task_guidance": {
                    "current_focus": "エラー復旧",
                    "next_actions": ["エラー詳細確認", "設定見直し", "パイプライン再起動"],
                    "priority_level": "high"
                },
                "context_state": {
                    "session_id": session_id if 'session_id' in locals() else "unknown",
                    "error": str(e)
                },
                "performance_metrics": {
                    "processing_time_seconds": round(processing_time, 3),
                    "optimization_status": "❌ エラー発生",
                    "pipeline_version": "v2.0_optimized"
                }
            }
    
    def _generate_task_guidance(self, context_store, intent_result, keywords) -> Dict[str, Any]:
        """Generate task execution guidance based on context analysis"""
        
        guidance = {
            "current_focus": "",
            "next_actions": [],
            "priority_level": "medium",
            "context_awareness": {}
        }
        
        # Analyze intent to provide guidance
        if "PROBLEM_DEFINITION" in intent_result.intent:
            guidance["current_focus"] = "新しい課題の定義と理解"
            guidance["next_actions"] = [
                "課題の詳細を明確化",
                "要件と制約を整理",
                "解決アプローチを検討"
            ]
            guidance["priority_level"] = "high"
            
        elif "CONSTRAINT_ADDITION" in intent_result.intent:
            guidance["current_focus"] = "制約条件の追加と適用"
            guidance["next_actions"] = [
                "新しい制約を既存計画に統合",
                "制約による影響を評価",
                "代替案を検討"
            ]
            guidance["priority_level"] = "high"
            
        elif "REFINEMENT" in intent_result.intent:
            guidance["current_focus"] = "要求の詳細化と改善"
            guidance["next_actions"] = [
                "既存要求を更新",
                "詳細仕様を作成",
                "実装計画を調整"
            ]
            guidance["priority_level"] = "medium"
            
        elif "QUESTION" in intent_result.intent:
            guidance["current_focus"] = "質問への回答と情報提供"
            guidance["next_actions"] = [
                "質問内容を分析",
                "関連情報を収集",
                "適切な回答を提供"
            ]
            guidance["priority_level"] = "medium"
            
        else:  # UNCLEAR
            guidance["current_focus"] = "発言内容の明確化"
            guidance["next_actions"] = [
                "追加情報を要求",
                "意図を確認",
                "具体例を求める"
            ]
            guidance["priority_level"] = "low"
        
        # Context awareness analysis
        core_context = context_store.core_context
        evolving_context = context_store.evolving_context
        
        guidance["context_awareness"] = {
            "has_core_problem": bool(core_context),
            "active_constraints": len(evolving_context),
            "conversation_continuity": len(context_store.turn_context) > 0,
            "key_topics": [kw["keyword"] for kw in keywords[:3]] if keywords else []
        }
        
        return guidance
    
    def _generate_optimized_task_guidance(self, context_store, intent_result, keywords) -> Dict[str, Any]:
        """⚡ 最適化された軽量タスクガイダンス生成 (0.01秒目標)"""
        
        # 🚀 高速インテント分析（辞書ルックアップベース）
        INTENT_TEMPLATES = {
            "PROBLEM_DEFINITION": {
                "current_focus": "新しい課題の定義と理解",
                "next_actions": ["課題の詳細を明確化", "要件と制約を整理", "解決アプローチを検討"],
                "priority_level": "high"
            },
            "CONSTRAINT_ADDITION": {
                "current_focus": "制約条件の追加と適用", 
                "next_actions": ["新しい制約を既存計画に統合", "制約による影響を評価", "代替案を検討"],
                "priority_level": "high"
            },
            "REFINEMENT": {
                "current_focus": "要求の詳細化と改善",
                "next_actions": ["既存要求を更新", "詳細仕様を作成", "実装計画を調整"],
                "priority_level": "medium"
            },
            "QUESTION": {
                "current_focus": "質問への回答と情報提供",
                "next_actions": ["質問内容を分析", "関連情報を収集", "適切な回答を提供"], 
                "priority_level": "medium"
            },
            "UNCLEAR": {
                "current_focus": "発言内容の明確化",
                "next_actions": ["追加情報を要求", "意図を確認", "具体例を求める"],
                "priority_level": "low"
            }
        }
        
        # 🎯 主要インテントの高速特定
        primary_intent = intent_result.intent[0] if intent_result.intent else "UNCLEAR"
        guidance = INTENT_TEMPLATES.get(primary_intent, INTENT_TEMPLATES["UNCLEAR"]).copy()
        
        # ⚡ 軽量文脈認識分析
        guidance["context_awareness"] = {
            "has_core_problem": bool(context_store.core_context),
            "active_constraints": len(context_store.evolving_context),
            "conversation_continuity": len(context_store.turn_context) > 0,
            "key_topics": [kw["keyword"] for kw in keywords[:3]] if keywords else []
        }
        
        return guidance
    
    async def close(self):
        """Clean up resources"""
        try:
            await self.classifier.close()
        except Exception:
            pass
        
        if self.http_client:
            try:
                await self.http_client.aclose()
            except Exception:
                pass
            self.http_client = None


# Global server instance
server = CCMCPServer()

# Initialize FastMCP server with correct import
mcp = FastMCP("CC-MCP")


@mcp.tool()
async def process_user_message(message: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Process user message with context management.
    
    ⚠️ 重要: 正しい使い方
    1. 必ず最初に start_session() を呼んでセッションIDを取得
    2. そのセッションIDを session_id パラメータに指定して使用
    3. セッションIDなしで使うと毎回新規セッションが作成され、文脈が失われます！
    
    正しい使用例:
    1) session = await start_session()
    2) await process_user_message(message="...", session_id=session["session_id"])
    3) 同じsession_idを使い続けることで文脈を維持
    4) 最後に await end_session(session_id=session["session_id"])
    
    機能:
    - 意図分類による文脈理解
    - 階層的コンテキスト管理
    - キーワード抽出と分析
    - タスクガイダンス生成

    Args:
        message: The user's message to process
        session_id: Session identifier (⚠️ 必須推奨！start_session()で取得したIDを使用)

    Returns:
        Response with intent analysis, keywords, task guidance, and context state
    """
    return await server.process_user_message(message, session_id)


@mcp.tool()
async def export_context(session_id: str = "default") -> Dict[str, Any]:
    """
    Export the current conversation context as structured data.
    
    ⚠️ 注意: 有効なセッションIDが必要です
    start_session()で取得したセッションIDを使用してください。

    Args:
        session_id: Session identifier (start_session()で取得したID)

    Returns:
        Structured dict containing the context state and operation status
    """
    try:
        context_store = server.session_manager.get_context(session_id)
        if context_store is None:
            return {
                "success": False,
                "error": "Session not found",
                "error_code": "SESSION_NOT_FOUND",
                "data": None
            }
        
        context_data = json.loads(context_store.export_state())
        return {
            "success": True,
            "data": context_data,
            "metadata": {
                "session_id": session_id,
                "exported_at": context_data.get("core_context", {}).get("timestamp", "unknown"),
                "items_count": {
                    "core_items": 1 if context_data.get("core_context") else 0,
                    "evolving_items": len(context_data.get("evolving_context", [])),
                    "turn_items": len(context_data.get("turn_context", []))
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "EXPORT_FAILED",
            "data": None
        }


@mcp.tool()
async def import_context(json_state: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Import conversation context from JSON string.
    
    ⚠️ 注意: セッションにコンテキストをインポートします
    新規または既存のセッションIDを指定してください。
    新規セッションの場合は自動作成されます。

    Args:
        json_state: JSON string containing context state (export_contextで取得したdata)
        session_id: Session identifier (任意のID、存在しない場合は新規作成)

    Returns:
        Operation result with detailed status and imported data summary
    """
    try:
        context_store = server.session_manager.get_context(session_id)
        created_new_session = False
        
        if context_store is None:
            # Create new session if it doesn't exist
            session_id = server.session_manager.start_session()
            context_store = server.session_manager.get_context(session_id)
            created_new_session = True
        
        # Parse and validate the JSON
        try:
            parsed_data = json.loads(json_state)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON format: {str(e)}",
                "error_code": "INVALID_JSON",
                "session_id": session_id
            }
        
        import_success = context_store.import_state(json_state)
        
        if import_success:
            return {
                "success": True,
                "session_id": session_id,
                "created_new_session": created_new_session,
                "imported_data": {
                    "core_items": 1 if parsed_data.get("core_context") else 0,
                    "evolving_items": len(parsed_data.get("evolving_context", [])),
                    "turn_items": len(parsed_data.get("turn_context", []))
                },
                "message": "Context imported successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to import context data",
                "error_code": "IMPORT_FAILED",
                "session_id": session_id
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR",
            "session_id": session_id if 'session_id' in locals() else "unknown"
        }


@mcp.tool()
async def clear_context(session_id: str = "default") -> Dict[str, Any]:
    """
    Clear all stored conversation context (same as end_session).
    
    ⚠️ 注意: セッションを終了し、全コンテキストを削除します
    end_session()と同じ効果です。

    Args:
        session_id: Session identifier (start_session()で取得したID)

    Returns:
        Operation result with detailed status
    """
    try:
        # Get session stats before clearing
        context_store = server.session_manager.get_context(session_id)
        pre_clear_stats = None
        
        if context_store:
            pre_clear_stats = {
                "had_core_problem": context_store.core_context is not None,
                "evolving_items_count": len(context_store.evolving_context),
                "turn_items_count": len(context_store.turn_context)
            }
        
        clear_success = server.session_manager.end_session(session_id)
        
        if clear_success:
            return {
                "success": True,
                "session_id": session_id,
                "message": "Context cleared successfully",
                "cleared_data": pre_clear_stats or {"message": "Session was already empty"}
            }
        else:
            return {
                "success": False,
                "error": "Session not found or already cleared",
                "error_code": "SESSION_NOT_FOUND",
                "session_id": session_id
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "CLEAR_FAILED",
            "session_id": session_id
        }


@mcp.tool()
async def get_debug_info(message: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Get detailed debug information about intent analysis and context management.
    
    デバッグ用: メッセージの意図分類結果とコンテキスト状態を確認できます。
    セッションが存在しない場合は新規作成されます。

    Args:
        message: Message to analyze
        session_id: Session identifier (start_session()で取得したID推奨)

    Returns:
        Debug information including intent analysis and context state details
    """
    try:
        # Get or create session context
        context_store = server.session_manager.get_context(session_id)
        if context_store is None:
            session_id = server.session_manager.start_session()
            context_store = server.session_manager.get_context(session_id)
        
        # Get intent classification
        intent_result = await server.classifier.classify_intent(message)
        
        # Extract keywords using TF-IDF
        keywords = server.keyword_extractor.extract_keywords(message, top_k=5)
        
        # Generate task guidance
        task_guidance = server._generate_task_guidance(context_store, intent_result, keywords)
        
        # Get context summary
        context_summary = context_store.get_context_summary()
        
        return {
            "session_id": session_id,
            "message": message,
            "intent_classification": {
                "intent": intent_result.intent,
                "reason": intent_result.reason
            },
            "keyword_extraction": {
                "keywords": keywords,
                "extraction_method": "TF-IDF",
                "corpus_stats": server.keyword_extractor.get_corpus_stats()
            },
            "task_guidance": task_guidance,
            "context_summary": context_summary,
            "system_stats": {
                "classifier_model": server.classifier.model,
                "context_levels": ["core", "evolving", "turn"],
                "session_stats": server.session_manager.get_session_stats(session_id)
            }
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def start_session() -> Dict[str, Any]:
    """
    Start a new conversation session.
    
    🎯 重要: CC-MCPを使う最初のステップ！
    
    使用方法:
    1. このツールを最初に呼んでセッションを開始
    2. 返されたsession_idを保存
    3. 全てのprocess_user_message呼び出しでそのsession_idを使用
    4. 最後にend_session()でセッションを終了
    
    これにより長期対話でも文脈が完璧に維持されます。

    Returns:
        Operation result with new session_id (必ず保存して使用してください)
    """
    try:
        session_id = server.session_manager.start_session()
        return {
            "success": True,
            "session_id": session_id,
            "message": "New session started successfully",
            "session_info": {
                "created_at": "just_now",
                "initial_state": "empty",
                "available_operations": [
                    "process_user_message",
                    "export_context", 
                    "import_context",
                    "get_session_stats"
                ]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "SESSION_CREATE_FAILED",
            "session_id": None
        }


@mcp.tool()
async def end_session(session_id: str) -> Dict[str, Any]:
    """
    End a conversation session and clear its context.
    
    ⚠️ 重要: タスク完了時は必ず呼んでください
    セッションを終了しないとメモリリークの原因になります。

    Args:
        session_id: Session identifier (start_session()で取得したID)

    Returns:
        Operation result with detailed status
    """
    try:
        # Get session info before ending
        context_store = server.session_manager.get_context(session_id)
        session_existed = context_store is not None
        
        if session_existed:
            final_stats = {
                "had_core_problem": context_store.core_context is not None,
                "evolving_items_count": len(context_store.evolving_context),
                "turn_items_count": len(context_store.turn_context)
            }
        
        success = server.session_manager.end_session(session_id)
        
        if success:
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session ended successfully",
                "final_state": final_stats if session_existed else {"message": "Session was empty"}
            }
        else:
            return {
                "success": False,
                "error": "Session not found or already ended",
                "error_code": "SESSION_NOT_FOUND",
                "session_id": session_id
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "SESSION_END_FAILED",
            "session_id": session_id
        }


@mcp.tool()
async def list_sessions() -> Dict[str, Any]:
    """
    List all active sessions with detailed information.
    
    デバッグ用: 現在アクティブな全セッションを確認できます。
    未終了のセッションがある場合はend_session()で終了してください。

    Returns:
        Operation result with session list and metadata
    """
    try:
        sessions = server.session_manager.list_sessions()
        
        # Get detailed info for each session
        session_details = []
        for session_id in sessions:
            stats = server.session_manager.get_session_stats(session_id)
            if stats:
                session_details.append({
                    "session_id": session_id,
                    "has_core_problem": stats.get("has_core_problem", False),
                    "evolving_items_count": stats.get("evolving_items_count", 0),
                    "recent_messages_count": stats.get("recent_messages_count", 0),
                    "status": "active"
                })
        
        return {
            "success": True,
            "total_sessions": len(sessions),
            "active_sessions": sessions,
            "session_details": session_details,
            "summary": {
                "sessions_with_problems": len([s for s in session_details if s["has_core_problem"]]),
                "sessions_with_constraints": len([s for s in session_details if s["evolving_items_count"] > 0]),
                "empty_sessions": len([s for s in session_details if not s["has_core_problem"] and s["evolving_items_count"] == 0])
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "LIST_SESSIONS_FAILED",
            "active_sessions": [],
            "total_sessions": 0
        }


@mcp.tool()
async def get_session_stats(session_id: str) -> Dict[str, Any]:
    """
    Get statistics for a specific session.
    
    セッションの状態確認用: コンテキスト数、メッセージ数などを取得できます。

    Args:
        session_id: Session identifier (start_session()で取得したID)

    Returns:
        Session statistics or error if session not found
    """
    stats = server.session_manager.get_session_stats(session_id)
    return stats or {"error": "Session not found"}


def main():
    """Main entry point for the MCP server"""
    import sys
    global mcp
    
    print("🚀 Starting CC-MCP Server (Official MCP SDK)...")
    print("📋 Available tools:")
    print("  - process_user_message: Process user messages with context management")
    print("  - export_context: Export conversation context")  
    print("  - import_context: Import conversation context")
    print("  - clear_context: Clear all context")
    print("  - get_debug_info: Get debug information")
    print("  - start_session: Start new session")
    print("  - end_session: End session")
    print("  - list_sessions: List all sessions")
    print("  - get_session_stats: Get session statistics")
    
    # Check for HTTP mode argument
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Parse port from command line
        port = 8000
        mount_path = None
        
        if len(sys.argv) > 2:
            # Try to parse as port number first
            try:
                port = int(sys.argv[2])
                mount_path = sys.argv[3] if len(sys.argv) > 3 else None
            except ValueError:
                # If not a number, treat as mount_path
                mount_path = sys.argv[2]
        
        print(f"🌐 Running SSE HTTP server on port {port}")
        if mount_path:
            print(f"   Mount path: {mount_path}")
        
        # Create new FastMCP instance with custom port if different from default
        if port != 8000:
            # Re-initialize mcp with custom port
            mcp = FastMCP("CC-MCP", port=port)
            # Register all tools again
            register_tools()
        
        mcp.run(transport="sse", mount_path=mount_path)
    else:
        print("🌐 Running with stdio transport (standard MCP)")
        mcp.run()


def register_tools():
    """Register all MCP tools with the server (for HTTP mode only)"""
    # HTTP mode では新しい関数定義を登録する必要がある場合に使用
    # 現在は不要（main関数で既に定義済み）
    pass


if __name__ == "__main__":
    main()
