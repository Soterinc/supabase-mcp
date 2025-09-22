#!/usr/bin/env python3
"""
Test script for remote MCP server with LangChain
This demonstrates how to use your remote MCP server with LangChain
"""

import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def test_remote_mcp_with_openai():
    """Test remote MCP with OpenAI model"""
    print("🧪 Testing Remote MCP with OpenAI...")
    
    # Configure your remote MCP server
    mcp_servers = [
        {
            "type": "url",
            "url": "http://localhost:3000/mcp",
            "name": "kavion",
            "tool_configuration": {
                "enabled": True,
                "allowed_tools": ["execute_sql", "list_tables", "search_docs"],
            },
        }
    ]
    
    # Initialize LLM with remote MCP
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        betas=["mcp-client-2025-04-04"],
        mcp_servers=mcp_servers,
    )
    
    # Test query
    response = llm.invoke("List all my datasets")
    print("🤖 OpenAI Response:")
    print(response.content)

def test_remote_mcp_with_anthropic():
    """Test remote MCP with Anthropic Claude model"""
    print("\n🧪 Testing Remote MCP with Anthropic Claude...")
    
    # Configure your remote MCP server
    mcp_servers = [
        {
            "type": "url",
            "url": "http://localhost:3000/mcp",
            "name": "kavion",
            "tool_configuration": {
                "enabled": True,
                "allowed_tools": ["execute_sql", "list_tables", "search_docs"],
            },
        }
    ]
    
    # Initialize LLM with remote MCP
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        betas=["mcp-client-2025-04-04"],
        mcp_servers=mcp_servers,
    )
    
    # Test query
    response = llm.invoke("How many images do I have in the Valero Sim dataset?")
    print("🤖 Anthropic Response:")
    print(response.content)

def test_direct_http():
    """Test direct HTTP calls to the remote MCP server"""
    print("\n🧪 Testing Direct HTTP calls...")
    
    import requests
    
    # Test health check
    try:
        health_response = requests.get("http://localhost:3000/health")
        print(f"✅ Health check: {health_response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test tools list
    try:
        tools_response = requests.post("http://localhost:3000/mcp", json={
            "method": "tools/list"
        })
        tools = tools_response.json()
        print(f"✅ Available tools: {[tool.get('name') for tool in tools.get('result', {}).get('tools', [])]}")
    except Exception as e:
        print(f"❌ Tools list failed: {e}")
        return
    
    # Test SQL execution
    try:
        sql_response = requests.post("http://localhost:3000/mcp", json={
            "method": "tools/call",
            "params": {
                "name": "execute_sql",
                "arguments": {"query": "SELECT COUNT(*) FROM datasets;"}
            }
        })
        result = sql_response.json()
        print(f"✅ SQL result: {result}")
    except Exception as e:
        print(f"❌ SQL execution failed: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Remote MCP Tests for Cursor\n")
    
    # Test 1: Direct HTTP calls
    test_direct_http()
    
    # Test 2: Remote MCP with OpenAI (uncomment if you have OpenAI API key)
    # test_remote_mcp_with_openai()
    
    # Test 3: Remote MCP with Anthropic (uncomment if you have Anthropic API key)
    # test_remote_mcp_with_anthropic()
    
    print("\n✅ All tests completed!")
    print("\n📋 To use in Cursor:")
    print("1. Make sure your remote MCP server is running: node simple-server.cjs")
    print("2. Copy the mcp.json file to your Cursor configuration")
    print("3. Restart Cursor")
    print("4. Ask Cursor: 'List all my datasets' or 'How many images do I have?'")

if __name__ == "__main__":
    main()