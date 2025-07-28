#!/usr/bin/env python3
"""
Simple test client for SSE MCP server
"""
import asyncio
import httpx
import json


async def test_sse_client():
    """Test the SSE MCP server"""
    url = "http://127.0.0.1:8001/sse/"
    
    async with httpx.AsyncClient() as client:
        # Test basic server connection
        try:
            response = await client.get(url)
            print(f"✅ Server is running on {url}")
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return
        
        # Test MCP capabilities endpoint
        try:
            capabilities_response = await client.post(
                url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    }
                }
            )
            print(f"✅ Initialize response: {capabilities_response.status_code}")
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")


if __name__ == "__main__":
    asyncio.run(test_sse_client())