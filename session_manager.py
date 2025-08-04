"""
Session Manager for CC-MCP Server
セッションIDベースの状態管理システム
"""
import uuid
from typing import Dict, Optional
from context_store import HierarchicalContextStore
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """
    セッションマネージャー
    各対話セッションを一意に識別し、セッションごとのコンテキストストアを管理する
    """
    
    def __init__(self):
        # セッションIDをキーとしたコンテキストストアの辞書
        self._sessions: Dict[str, HierarchicalContextStore] = {}
        logger.info("SessionManager initialized")
    
    def start_session(self) -> str:
        """
        新規セッションを開始し、ユニークなsession_idを発行する。
        同時に、そのセッションIDに紐づく空の「階層型コンテキストストア」を生成・保持する。
        
        Returns:
            str: ユニークなセッションID
        """
        session_id = str(uuid.uuid4())
        
        # 新しいコンテキストストアを作成
        context_store = HierarchicalContextStore()
        self._sessions[session_id] = context_store
        
        logger.info(f"New session started: {session_id}")
        return session_id
    
    def get_context(self, session_id: str) -> Optional[HierarchicalContextStore]:
        """
        指定されたsession_idに対応するコンテキストストアを取得する。
        
        Args:
            session_id: セッションID
            
        Returns:
            HierarchicalContextStore or None: 対応するコンテキストストア
        """
        context_store = self._sessions.get(session_id)
        
        if context_store is None:
            logger.warning(f"Session not found: {session_id}")
        
        return context_store
    
    def end_session(self, session_id: str) -> bool:
        """
        セッションを終了し、関連するコンテキストストアを破棄する。
        
        Args:
            session_id: セッションID
            
        Returns:
            bool: 正常に終了した場合True、セッションが存在しない場合False
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Session ended: {session_id}")
            return True
        else:
            logger.warning(f"Session not found for termination: {session_id}")
            return False
    
    def list_sessions(self) -> list[str]:
        """
        現在アクティブなセッションIDのリストを取得する
        
        Returns:
            list[str]: アクティブなセッションIDのリスト
        """
        return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """
        現在アクティブなセッション数を取得する
        
        Returns:
            int: アクティブなセッション数
        """
        return len(self._sessions)
    
    def session_exists(self, session_id: str) -> bool:
        """
        指定されたセッションIDが存在するかチェックする
        
        Args:
            session_id: セッションID
            
        Returns:
            bool: セッションが存在する場合True
        """
        return session_id in self._sessions
    
    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """
        セッションの統計情報を取得する
        
        Args:
            session_id: セッションID
            
        Returns:
            dict or None: セッション統計情報
        """
        context_store = self.get_context(session_id)
        
        if context_store is None:
            return None
        
        context_summary = context_store.get_context_summary()
        
        return {
            "session_id": session_id,
            "has_core_problem": context_summary["core_problem"] is not None,
            "evolving_items_count": len(context_summary["evolving_items"]),
            "recent_messages_count": len(context_summary["recent_conversation"].split("\n")) if context_summary["recent_conversation"] else 0,
            "total_keywords": len(context_summary.get("core_keywords", [])) + len(context_summary.get("evolving_keywords", []))
        }
