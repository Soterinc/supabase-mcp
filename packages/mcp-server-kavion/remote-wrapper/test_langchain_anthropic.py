#!/usr/bin/env python3
"""
LangChain Anthropic Remote MCP Client
This client uses LangChain with Anthropic and your remote MCP server
"""
import os
import sys
from langchain_anthropic import ChatAnthropic

def test_anthropic_remote_mcp():
    """Test Anthropic with remote MCP server"""
    print("🚀 Testing Anthropic with Remote MCP Server")
    print("=" * 50)
    
    # Check if Anthropic API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set. Please set it to test Anthropic.")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Initialize Anthropic LLM with remote MCP
    mcp_servers = [
        {
            "type": "url",
            "url": "http://localhost:3000/mcp",
            "name": "kavion",
            "tool_configuration": {
                "enabled": True,
                "allowed_tools": ["execute_sql", "list_tables", "search_docs", "get_quick_stats"],
            },
        }
    ]
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        betas=["mcp-client-2025-04-04"],
        mcp_servers=mcp_servers,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Test query
    query = "List all my datasets"
    print(f"🔍 Query: {query}")
    
    try:
        response = llm.invoke(query)
        print(f"✅ Response: {response.content}")
        
        # Check for tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🔧 Tool calls: {response.tool_calls}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🎯 LangChain Anthropic Remote MCP Test")
    print("=" * 60)
    
    # Check if remote server is running
    import requests
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Remote MCP server is not running. Please start it with: node working_server.cjs")
            return
    except Exception as e:
        print(f"❌ Cannot connect to remote MCP server: {e}")
        print("Please start the server with: node working_server.cjs")
        return
    
    # Test Anthropic if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        test_anthropic_remote_mcp()
    else:
        print("\n⚠️  ANTHROPIC_API_KEY not set, skipping Anthropic test")
        print("To test Anthropic, set your API key: export ANTHROPIC_API_KEY='your-key-here'")

if __name__ == "__main__":
    main()