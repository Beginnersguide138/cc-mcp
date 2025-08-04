from typing import Dict, Any, Optional
from context_store import HierarchicalContextStore


class PromptSynthesisEngine:
    """
    Prompt Synthesis Engine that constructs the final prompt for the main LLM
    by combining information from all context store levels.
    """
    
    PROMPT_TEMPLATE = """# Mission (あなたの使命)
あなたはユーザーの課題解決を支援するAIアシスタントです。以下の核となる目的を常に念頭に置いてください。

{core_context}

# Constraints (遵守すべき制約と決定事項)
以下の条件を必ず満たすように応答を生成してください。
{evolving_context}

# Recent Conversation (直近の会話)
{turn_context}

# User's Current Message (ユーザーの現在のメッセージ)
{current_message}"""

    def __init__(self, context_store: HierarchicalContextStore):
        self.context_store = context_store
    
    def synthesize_prompt(self, current_message: str) -> str:
        """
        Synthesize the final prompt by combining context from all levels.
        
        Args:
            current_message: The user's current message
            
        Returns:
            The synthesized prompt ready for the main LLM
        """
        context_summary = self.context_store.get_context_summary()
        
        # Format core context
        core_context = self._format_core_context(context_summary["core_problem"])
        
        # Format evolving context
        evolving_context = self._format_evolving_context(context_summary["evolving_items"])
        
        # Format turn context
        turn_context = self._format_turn_context(context_summary["recent_conversation"])
        
        # Synthesize final prompt
        return self.PROMPT_TEMPLATE.format(
            core_context=core_context,
            evolving_context=evolving_context,
            turn_context=turn_context,
            current_message=current_message
        )
    
    def _format_core_context(self, core_problem: Optional[str]) -> str:
        """Format the core context section"""
        if core_problem is None:
            return "（まだ明確な課題が定義されていません。ユーザーの課題を理解し、支援することを目指してください。）"
        
        # Add keywords if available
        context_summary = self.context_store.get_context_summary()
        core_keywords_text = self.context_store.get_core_keywords_text() if hasattr(self.context_store, 'get_core_keywords_text') else ""
        
        formatted = f"**主要課題**: {core_problem}"
        if core_keywords_text:
            formatted += f"\n{core_keywords_text}"
        
        return formatted
    
    def _format_evolving_context(self, evolving_items: list) -> str:
        """Format the evolving context section"""
        if not evolving_items:
            return "（現在、特別な制約や決定事項はありません。）"
        
        formatted_items = []
        for item in evolving_items:
            formatted_items.append(f"- {item}")
        
        # Add evolving keywords if available
        evolving_keywords_text = self.context_store.get_evolving_keywords_text() if hasattr(self.context_store, 'get_evolving_keywords_text') else ""
        
        result = "\n".join(formatted_items)
        if evolving_keywords_text:
            result += f"\n\n{evolving_keywords_text}"
        
        return result
    
    def _format_turn_context(self, recent_conversation: str) -> str:
        """Format the turn context section"""
        if not recent_conversation.strip():
            return "（これが対話の開始です。）"
        
        return recent_conversation
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about the current context state"""
        context_summary = self.context_store.get_context_summary()
        
        return {
            "has_core_problem": context_summary["core_problem"] is not None,
            "evolving_items_count": len(context_summary["evolving_items"]),
            "recent_messages_count": len(context_summary["recent_conversation"].split("\n")) if context_summary["recent_conversation"] else 0
        }
    
    def create_debug_info(self, current_message: str) -> Dict[str, Any]:
        """Create debug information about the prompt synthesis process"""
        context_summary = self.context_store.get_context_summary()
        synthesized_prompt = self.synthesize_prompt(current_message)
        
        return {
            "input": {
                "current_message": current_message,
                "context_summary": context_summary
            },
            "processing": {
                "core_formatted": self._format_core_context(context_summary["core_problem"]),
                "evolving_formatted": self._format_evolving_context(context_summary["evolving_items"]),
                "turn_formatted": self._format_turn_context(context_summary["recent_conversation"])
            },
            "output": {
                "synthesized_prompt": synthesized_prompt,
                "prompt_length": len(synthesized_prompt),
                "stats": self.get_context_stats()
            }
        }
