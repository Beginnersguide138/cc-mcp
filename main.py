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
        """Process a user message through the MCP system."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Starting process_user_message for session: {session_id}")
            
            # Step 1: Get or create session context
            context_store = self.session_manager.get_context(session_id)
            if context_store is None:
                # Start new session if it doesn't exist
                session_id = self.session_manager.start_session()
                context_store = self.session_manager.get_context(session_id)
                logger.info(f"Created new session: {session_id}")
            
            # Step 2: Intent Classification (TF-IDF + LLM classification)
            logger.info("Starting intent classification")
            intent_result = await self.classifier.classify_intent(message)
            logger.info(f"Intent classification complete: {intent_result.intent}")
            
            # Step 3: Extract keywords using TF-IDF
            logger.info("Extracting keywords using TF-IDF")
            keywords = self.keyword_extractor.extract_keywords(message, top_k=5)
            logger.info(f"Keywords extracted: {keywords}")
            
            # Step 4: Store in context with keywords
            logger.info("Storing message in context")
            context_store.store_message(
                content=message,
                intent_labels=intent_result.intent,
                role="user",
                keywords=keywords
            )
            
            # Step 5: Generate task execution guidance based on context analysis
            logger.info("Generating task execution guidance")
            task_guidance = self._generate_task_guidance(context_store, intent_result, keywords)
            logger.info("Task guidance generation complete")
            
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
                }
            }
            
            logger.info("Process complete, returning result")
            return result
            
        except Exception as e:
            logger.error(f"Error in process_user_message: {str(e)}", exc_info=True)
            return {
                "intent_analysis": {
                    "intent": ["ERROR"],
                    "reason": f"処理中にエラーが発生しました: {str(e)}",
                    "confidence": "low"
                },
                "keyword_analysis": [],
                "task_guidance": {
                    "current_focus": "エラー処理",
                    "next_actions": ["エラーの詳細を確認", "設定を見直し", "再試行"]
                },
                "context_state": {
                    "session_id": session_id if 'session_id' in locals() else "unknown",
                    "error": str(e)
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
    Process a user message through the MCP system.

    Args:
        message: The user's message to process
        session_id: Optional session identifier for context isolation

    Returns:
        Response from the AI assistant with processing metadata
    """
    return await server.process_user_message(message, session_id)


@mcp.tool()
async def export_context(session_id: str = "default") -> Dict[str, Any]:
    """
    Export the current conversation context as structured data.

    Args:
        session_id: Session identifier

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

    Args:
        json_state: JSON string containing context state
        session_id: Session identifier

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
    Clear all stored conversation context.

    Args:
        session_id: Session identifier

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

    Args:
        message: Message to analyze
        session_id: Session identifier

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

    Returns:
        Operation result with new session information
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

    Args:
        session_id: Session identifier

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

    Args:
        session_id: Session identifier

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
