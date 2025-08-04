"""
Hierarchical Context Store for CC-MCP Server v1.3
階層型コンテキストストア（キーワード抽出対応）
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Message:
    """Represents a single message in the conversation"""
    content: str
    role: str  # "user" or "assistant"
    timestamp: datetime
    intent_labels: List[str]

@dataclass
class ContextItem:
    """Represents a context item with content and keywords"""
    content: str
    keywords: List[Dict[str, float]]  # [{"keyword": "word", "score": 0.123}, ...]
    timestamp: datetime
    intent_labels: List[str]

class HierarchicalContextStore:
    """
    Hierarchical Context Store that manages conversation context across three levels:
    - Core Context (Long-term memory): Problem definitions with keywords
    - Evolving Context (Medium-term memory): Constraints and decisions with keywords  
    - Turn Context (Short-term memory): Recent 2-3 conversation turns
    """
    
    def __init__(self):
        # Core Context: Stores the main problem/goal with keywords
        self.core_context: Optional[ContextItem] = None
        
        # Evolving Context: Stores constraints, decisions, and refinements with keywords
        self.evolving_context: List[ContextItem] = []
        
        # Turn Context: Stores recent conversation history
        self.turn_context: List[Message] = []
        
        # Maximum number of messages to keep in turn context
        self.max_turn_context = 6  # 2-3 conversation turns (user + assistant pairs)
    
    def store_message(self, content: str, intent_labels: List[str], role: str = "user", keywords: Optional[List[Dict[str, float]]] = None) -> None:
        """
        Store a message in the appropriate context level based on intent labels
        
        Args:
            content: The message content
            intent_labels: List of intent classification labels
            role: The role of the message sender ("user" or "assistant")
            keywords: Optional extracted keywords for important messages
        """
        message = Message(
            content=content,
            role=role,
            timestamp=datetime.now(),
            intent_labels=intent_labels
        )
        
        # Always add to turn context
        self.turn_context.append(message)
        self._trim_turn_context()
        
        # Store in appropriate long-term context based on intent
        if role == "user":  # Only process user messages for long-term storage
            if "PROBLEM_DEFINITION" in intent_labels:
                self.core_context = ContextItem(
                    content=content,
                    keywords=keywords or [],
                    timestamp=datetime.now(),
                    intent_labels=intent_labels
                )
            
            if "CONSTRAINT_ADDITION" in intent_labels or "REFINEMENT" in intent_labels:
                context_item = ContextItem(
                    content=content,
                    keywords=keywords or [],
                    timestamp=datetime.now(),
                    intent_labels=intent_labels
                )
                self.evolving_context.append(context_item)
    
    def _trim_turn_context(self) -> None:
        """Keep only the most recent messages in turn context"""
        if len(self.turn_context) > self.max_turn_context:
            self.turn_context = self.turn_context[-self.max_turn_context:]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all context levels
        
        Returns:
            Dict containing summaries of all context levels
        """
        # Format recent conversation
        recent_conversation = ""
        for msg in self.turn_context[-4:]:  # Last 4 messages
            recent_conversation += f"{msg.role}: {msg.content}\n"
        
        # Extract core keywords
        core_keywords = []
        if self.core_context:
            core_keywords = self.core_context.keywords
        
        # Extract evolving keywords
        evolving_keywords = []
        for item in self.evolving_context:
            evolving_keywords.extend(item.keywords)
        
        return {
            "core_problem": self.core_context.content if self.core_context else None,
            "evolving_items": [item.content for item in self.evolving_context],
            "recent_conversation": recent_conversation.strip(),
            "core_keywords": core_keywords,
            "evolving_keywords": evolving_keywords
        }
    
    def get_core_keywords_text(self) -> str:
        """Get core keywords as formatted text"""
        if not self.core_context or not self.core_context.keywords:
            return ""
        
        keywords = [kw["keyword"] for kw in self.core_context.keywords[:5]]  # Top 5
        return f"重要キーワード: {', '.join(keywords)}"
    
    def get_evolving_keywords_text(self) -> str:
        """Get evolving keywords as formatted text"""
        all_keywords = []
        for item in self.evolving_context:
            for kw in item.keywords[:3]:  # Top 3 per item
                all_keywords.append(kw["keyword"])
        
        if not all_keywords:
            return ""
        
        # Remove duplicates while preserving order
        unique_keywords = list(dict.fromkeys(all_keywords))
        return f"制約・詳細キーワード: {', '.join(unique_keywords[:8])}"  # Max 8 keywords
    
    def export_state(self) -> str:
        """
        Export the current context state as JSON string
        
        Returns:
            JSON string representation of the context state
        """
        state = {
            "core_context": {
                "content": self.core_context.content,
                "keywords": self.core_context.keywords,
                "timestamp": self.core_context.timestamp.isoformat(),
                "intent_labels": self.core_context.intent_labels
            } if self.core_context else None,
            "evolving_context": [
                {
                    "content": item.content,
                    "keywords": item.keywords,
                    "timestamp": item.timestamp.isoformat(),
                    "intent_labels": item.intent_labels
                }
                for item in self.evolving_context
            ],
            "turn_context": [
                {
                    "content": msg.content,
                    "role": msg.role,
                    "timestamp": msg.timestamp.isoformat(),
                    "intent_labels": msg.intent_labels
                }
                for msg in self.turn_context
            ]
        }
        return json.dumps(state, ensure_ascii=False, indent=2)
    
    def import_state(self, json_state: str) -> bool:
        """
        Import context state from JSON string
        
        Args:
            json_state: JSON string representation of the context state
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            state = json.loads(json_state)
            
            # Import core context
            core_data = state.get("core_context")
            if core_data:
                self.core_context = ContextItem(
                    content=core_data["content"],
                    keywords=core_data["keywords"],
                    timestamp=datetime.fromisoformat(core_data["timestamp"]),
                    intent_labels=core_data["intent_labels"]
                )
            else:
                self.core_context = None
            
            # Import evolving context
            self.evolving_context = []
            for item_data in state.get("evolving_context", []):
                context_item = ContextItem(
                    content=item_data["content"],
                    keywords=item_data["keywords"],
                    timestamp=datetime.fromisoformat(item_data["timestamp"]),
                    intent_labels=item_data["intent_labels"]
                )
                self.evolving_context.append(context_item)
            
            # Import turn context
            self.turn_context = []
            for msg_data in state.get("turn_context", []):
                message = Message(
                    content=msg_data["content"],
                    role=msg_data["role"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    intent_labels=msg_data["intent_labels"]
                )
                self.turn_context.append(message)
            
            return True
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return False
    
    def clear_all(self) -> None:
        """Clear all stored context"""
        self.core_context = None
        self.evolving_context = []
        self.turn_context = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics"""
        return {
            "has_core_problem": self.core_context is not None,
            "evolving_items_count": len(self.evolving_context),
            "recent_messages_count": len(self.turn_context),
            "total_keywords": len(self.get_context_summary().get("core_keywords", [])) + len(self.get_context_summary().get("evolving_keywords", []))
        }
