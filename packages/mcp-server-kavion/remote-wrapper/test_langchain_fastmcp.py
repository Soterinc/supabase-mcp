#!/usr/bin/env python3
"""
Test FastMCP Server with LangChain
This script tests your FastMCP server using LangChain's remote MCP support
"""
import os
import sys
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def test_openai_with_fastmcp():
    """Test OpenAI with FastMCP server"""
    print("🚀 Testing OpenAI with FastMCP Server")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please set it to test OpenAI.")
        print("   export OPENAI_API_KEY='your-key-here'")
        return None
    
    # Initialize OpenAI LLM with remote MCP
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        output_version="responses/v1",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Bind remote MCP tools
    llm_with_tools = llm.bind_tools([
        {
            "type": "mcp",
            "server_label": "kavion",
            "server_url": "http://localhost:8000/sse/",
            "require_approval": "never",
        }
    ])
    
    # Test queries
    test_queries = [
        "List all my datasets",
        "How many images are in the Valero Sim dataset?",
        "Show me the database tables"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            response = llm_with_tools.invoke(query)
            print(f"✅ Response: {response.content}")
            
            # Check for tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Tool calls: {response.tool_calls}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return llm_with_tools

def test_anthropic_with_fastmcp():
    """Test Anthropic with FastMCP server"""
    print("\n🚀 Testing Anthropic with FastMCP Server")
    print("=" * 50)
    
    # Check if Anthropic API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set. Please set it to test Anthropic.")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        return None
    
    # Initialize Anthropic LLM with remote MCP
    mcp_servers = [
        {
            "type": "url",
            "url": "http://localhost:8000/sse/",
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
    
    # Test queries
    test_queries = [
        "List all my datasets",
        "How many images are in the Valero Sim dataset?",
        "Show me the database tables"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            response = llm.invoke(query)
            print(f"✅ Response: {response.content}")
            
            # Check for tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Tool calls: {response.tool_calls}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return llm

def test_direct_fastmcp():
    """Test FastMCP server directly without LangChain"""
    print("\n🚀 Testing FastMCP Server Directly")
    print("=" * 50)
    
    import requests
    import json
    import uuid
    
    # Get session ID from SSE endpoint
    try:
        response = requests.get("http://localhost:8000/sse/", timeout=5)
        if response.status_code == 200:
            print("✅ FastMCP server is running")
            
            # Parse the SSE response to get session ID
            lines = response.text.split('\n')
            session_id = None
            for line in lines:
                if line.startswith('data: /messages/?session_id='):
                    session_id = line.split('session_id=')[1]
                    break
            
            if session_id:
                print(f"📡 Session ID: {session_id}")
                print(f"📡 Messages endpoint: http://localhost:8000/sse/messages/?session_id={session_id}")
            else:
                print("❌ Could not get session ID")
                return
        else:
            print(f"❌ FastMCP server error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to FastMCP server: {e}")
        return
    
    # Test MCP tools
    test_tools = [
        {
            "name": "execute_sql",
            "args": {"query": "SELECT id, name, description FROM datasets LIMIT 3;"}
        },
        {
            "name": "list_tables",
            "args": {"schemas": ["public"]}
        }
    ]
    
    for tool in test_tools:
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool["name"],
                    "arguments": tool["args"]
                }
            }
            
            print(f"\n🧪 Testing {tool['name']} tool...")
            response = requests.post(
                f"http://localhost:8000/sse/messages/?session_id={session_id}", 
                json=request, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {tool['name']} successful!")
                print(f"📊 Result: {str(result)[:500]}...")
            else:
                print(f"❌ {tool['name']} failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {tool['name']} error: {e}")

def main():
    print("🎯 FastMCP Server Test Suite")
    print("=" * 60)
    
    # Check if FastMCP server is running
    import requests
    try:
        response = requests.get("http://localhost:8000/sse/", timeout=5)
        if response.status_code != 200:
            print("❌ FastMCP server is not running. Please start it with: python3 fastmcp_server.py")
            return
    except Exception as e:
        print(f"❌ Cannot connect to FastMCP server: {e}")
        print("Please start the server with: python3 fastmcp_server.py")
        return
    
    # Test direct FastMCP connection
    test_direct_fastmcp()
    
    # Test with OpenAI if API key is available
    if os.getenv("OPENAI_API_KEY"):
        test_openai_with_fastmcp()
    else:
        print("\n⚠️  OPENAI_API_KEY not set, skipping OpenAI test")
        print("To test OpenAI, set your API key: export OPENAI_API_KEY='your-key-here'")
    
    # Test with Anthropic if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        test_anthropic_with_fastmcp()
    else:
        print("\n⚠️  ANTHROPIC_API_KEY not set, skipping Anthropic test")
        print("To test Anthropic, set your API key: export ANTHROPIC_API_KEY='your-key-here'")

if __name__ == "__main__":
    main()
