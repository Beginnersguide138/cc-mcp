from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Message:
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoreContext:
    """Long-term memory for problem definition"""
    problem_definition: Optional[Message] = None
    
    def set_problem(self, message: Message):
        """Set the core problem definition"""
        self.problem_definition = message
    
    def get_problem(self) -> Optional[str]:
        """Get the problem definition text"""
        return self.problem_definition.content if self.problem_definition else None


@dataclass
class EvolvingContext:
    """Medium-term memory for constraints and refinements"""
    constraints: List[Message] = field(default_factory=list)
    refinements: List[Message] = field(default_factory=list)
    
    def add_constraint(self, message: Message):
        """Add a new constraint"""
        self.constraints.append(message)
    
    def add_refinement(self, message: Message):
        """Add a new refinement"""
        self.refinements.append(message)
    
    def get_all_items(self) -> List[str]:
        """Get all constraints and refinements as text list"""
        items = []
        for constraint in self.constraints:
            items.append(f"制約: {constraint.content}")
        for refinement in self.refinements:
            items.append(f"詳細化: {refinement.content}")
        return items


@dataclass
class TurnContext:
    """Short-term memory for recent conversation turns"""
    messages: List[Message] = field(default_factory=list)
    max_turns: int = 3
    
    def add_message(self, message: Message):
        """Add a message and maintain max_turns limit"""
        self.messages.append(message)
        if len(self.messages) > self.max_turns:
            self.messages = self.messages[-self.max_turns:]
    
    def get_recent_conversation(self) -> str:
        """Get recent conversation as formatted text"""
        if not self.messages:
            return ""
        
        conversation = []
        for msg in self.messages:
            role = msg.metadata.get("role", "user")
            conversation.append(f"{role}: {msg.content}")
        
        return "\n".join(conversation)


class HierarchicalContextStore:
    """
    Hierarchical Context Store that manages three levels of memory:
    - Core Context (long-term): Problem definitions
    - Evolving Context (medium-term): Constraints and refinements
    - Turn Context (short-term): Recent conversation history
    """
    
    def __init__(self):
        self.core = CoreContext()
        self.evolving = EvolvingContext()
        self.turn = TurnContext()
    
    def store_message(self, content: str, intent_labels: List[str], role: str = "user") -> None:
        """
        Store a message in the appropriate context based on intent labels.
        
        Args:
            content: The message content
            intent_labels: List of intent labels from the classifier
            role: The role of the message sender (user/assistant)
        """
        message = Message(
            content=content,
            metadata={"role": role, "intent": intent_labels}
        )
        
        # Always add to turn context for conversation flow
        self.turn.add_message(message)
        
        # Store in appropriate long/medium-term context based on intent
        if "PROBLEM_DEFINITION" in intent_labels:
            self.core.set_problem(message)
        
        if "CONSTRAINT_ADDITION" in intent_labels:
            self.evolving.add_constraint(message)
        
        if "REFINEMENT" in intent_labels:
            self.evolving.add_refinement(message)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of all context levels"""
        return {
            "core_problem": self.core.get_problem(),
            "evolving_items": self.evolving.get_all_items(),
            "recent_conversation": self.turn.get_recent_conversation()
        }
    
    def export_state(self) -> str:
        """Export the entire context store state as JSON"""
        def serialize_message(msg: Optional[Message]) -> Optional[Dict]:
            if msg is None:
                return None
            return {
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
        
        def serialize_messages(messages: List[Message]) -> List[Dict]:
            return [serialize_message(msg) for msg in messages]
        
        state = {
            "core": {
                "problem_definition": serialize_message(self.core.problem_definition)
            },
            "evolving": {
                "constraints": serialize_messages(self.evolving.constraints),
                "refinements": serialize_messages(self.evolving.refinements)
            },
            "turn": {
                "messages": serialize_messages(self.turn.messages),
                "max_turns": self.turn.max_turns
            }
        }
        
        return json.dumps(state, indent=2, ensure_ascii=False)
    
    def import_state(self, json_state: str) -> None:
        """Import context store state from JSON"""
        def deserialize_message(data: Optional[Dict]) -> Optional[Message]:
            if data is None:
                return None
            return Message(
                content=data["content"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                metadata=data.get("metadata", {})
            )
        
        def deserialize_messages(data: List[Dict]) -> List[Message]:
            return [deserialize_message(item) for item in data if item is not None]
        
        try:
            state = json.loads(json_state)
            
            # Restore core context
            self.core.problem_definition = deserialize_message(
                state.get("core", {}).get("problem_definition")
            )
            
            # Restore evolving context
            evolving_data = state.get("evolving", {})
            self.evolving.constraints = deserialize_messages(
                evolving_data.get("constraints", [])
            )
            self.evolving.refinements = deserialize_messages(
                evolving_data.get("refinements", [])
            )
            
            # Restore turn context
            turn_data = state.get("turn", {})
            self.turn.messages = deserialize_messages(
                turn_data.get("messages", [])
            )
            self.turn.max_turns = turn_data.get("max_turns", 3)
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to import context state: {str(e)}")
    
    def clear_all(self) -> None:
        """Clear all stored context"""
        self.core = CoreContext()
        self.evolving = EvolvingContext()
        self.turn = TurnContext()