import asyncio
import json
import os
from typing import Dict, Any, Optional
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from intent_classifier import IntentClassifier
from context_store import HierarchicalContextStore
from prompt_synthesis import PromptSynthesisEngine


class MCPServer:
    """
    Main MCP Server that orchestrates intelligent context management
    for long-term dialogue consistency.
    """
    
    def __init__(self):
        # Initialize components
        self.context_store = HierarchicalContextStore()
        self.prompt_engine = PromptSynthesisEngine(self.context_store)
        
        # Initialize intent classifier (will be configured via environment variables)
        classifier_api_url = os.getenv("CLASSIFIER_API_URL", "https://api.openai.com/v1/chat/completions")
        classifier_api_key = os.getenv("CLASSIFIER_API_KEY", "")
        classifier_model = os.getenv("CLASSIFIER_MODEL", "gpt-3.5-turbo")
        
        self.intent_classifier = IntentClassifier(
            api_url=classifier_api_url,
            api_key=classifier_api_key,
            model=classifier_model
        )
        
        # Main LLM configuration
        self.main_api_url = os.getenv("MAIN_API_URL", "https://api.openai.com/v1/chat/completions")
        self.main_api_key = os.getenv("MAIN_API_KEY", "")
        self.main_model = os.getenv("MAIN_MODEL", "gpt-4")
        self.main_temperature = float(os.getenv("MAIN_TEMPERATURE", "0.7"))
        
        self.http_client = httpx.AsyncClient()
    
    async def process_message(self, user_message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user message through the complete MCP pipeline.
        
        Args:
            user_message: The user's input message
            session_id: Session identifier for context isolation
            
        Returns:
            Dictionary containing the response and processing metadata
        """
        try:
            # Step 1: Classify intent
            intent_result = await self.intent_classifier.classify_intent(user_message)
            
            # Step 2: Store in context based on intent
            self.context_store.store_message(
                content=user_message,
                intent_labels=intent_result.intent,
                role="user"
            )
            
            # Step 3: Synthesize prompt with context
            synthesized_prompt = self.prompt_engine.synthesize_prompt(user_message)
            
            # Step 4: Generate response from main LLM
            main_response = await self._call_main_llm(synthesized_prompt)
            
            # Step 5: Store assistant response in turn context
            self.context_store.store_message(
                content=main_response,
                intent_labels=["RESPONSE"],
                role="assistant"
            )
            
            return {
                "response": main_response,
                "metadata": {
                    "intent_classification": {
                        "intent": intent_result.intent,
                        "reason": intent_result.reason
                    },
                    "context_stats": self.prompt_engine.get_context_stats(),
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            return {
                "response": "申し訳ございませんが、処理中にエラーが発生しました。もう一度お試しください。",
                "metadata": {
                    "error": str(e),
                    "session_id": session_id
                }
            }
    
    async def _call_main_llm(self, prompt: str) -> str:
        """Call the main LLM with the synthesized prompt"""
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_completion_tokens": 2000
        }
        
        headers = {
            "api-key": self.main_api_key,
            "Content-Type": "application/json"
        }
        
        response = await self.http_client.post(
            self.main_api_url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    async def get_context_export(self, session_id: str = "default") -> str:
        """Export the current context state as JSON"""
        return self.context_store.export_state()
    
    async def import_context(self, json_state: str, session_id: str = "default") -> bool:
        """Import context state from JSON"""
        try:
            self.context_store.import_state(json_state)
            return True
        except Exception:
            return False
    
    async def clear_context(self, session_id: str = "default") -> bool:
        """Clear all stored context"""
        try:
            self.context_store.clear_all()
            return True
        except Exception:
            return False
    
    async def close(self):
        """Clean up resources"""
        await self.intent_classifier.close()
        await self.http_client.aclose()


# Initialize FastMCP server
mcp = FastMCP(name="CC-MCP")
server = MCPServer()


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
    return await server.process_message(message, session_id)


@mcp.tool()
async def export_context(session_id: str = "default") -> str:
    """
    Export the current conversation context as JSON.
    
    Args:
        session_id: Session identifier
    
    Returns:
        JSON string containing the context state
    """
    return await server.get_context_export(session_id)


@mcp.tool()
async def import_context(json_state: str, session_id: str = "default") -> bool:
    """
    Import conversation context from JSON.
    
    Args:
        json_state: JSON string containing context state
        session_id: Session identifier
    
    Returns:
        True if import was successful, False otherwise
    """
    return await server.import_context(json_state, session_id)


@mcp.tool()
async def clear_context(session_id: str = "default") -> bool:
    """
    Clear all stored conversation context.
    
    Args:
        session_id: Session identifier
    
    Returns:
        True if clear was successful, False otherwise
    """
    return await server.clear_context(session_id)


@mcp.tool()
async def get_debug_info(message: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Get detailed debug information about prompt synthesis.
    
    Args:
        message: Message to analyze
        session_id: Session identifier
    
    Returns:
        Debug information including context analysis and prompt synthesis details
    """
    return server.prompt_engine.create_debug_info(message)


def main():
    """Main entry point for the MCP server"""
    print("🚀 Starting CC-MCP Server...")
    print("📋 Available tools:")
    print("  - process_user_message: Process user messages with context management")
    print("  - export_context: Export conversation context")
    print("  - import_context: Import conversation context")
    print("  - clear_context: Clear all context")
    print("  - get_debug_info: Get debug information")
    
    # Use mcp.run() directly without asyncio.run() to avoid nested event loop
    mcp.run(transport='sse', port=8001)


if __name__ == "__main__":
    main()
