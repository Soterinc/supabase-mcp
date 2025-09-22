#!/usr/bin/env python3
"""
Cursor MCP Test Script
This script demonstrates how to use the Kavion MCP server in Cursor
"""

import asyncio
import json
from pathlib import Path

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# MCP imports
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def get_kavion_server_params() -> StdioServerParameters:
    """Get the Node.js MCP server parameters for kavion-thermal-jwt."""
    return StdioServerParameters(
        command="node",
        args=[
            "/home/behnam/git/KavApps/kavion-v0/supabase-mcp/packages/mcp-server-kavion/dist/transports/stdio.js",
            "--read-only",
            "--features=database,docs",
            "--user-email=behnammoradi026@gmail.com",
            "--user-password=Behnam1993!"
        ],
        env={
            "SUPABASE_URL": "https://vwovgsttefakrjcaytin.supabase.co",
            "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3b3Znc3R0ZWZha3JqY2F5dGluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NTgxNDUsImV4cCI6MjA2MzMzNDE0NX0.3ZzaKTX6PS68f8-VPkwqr5ng4-Iwu5_aNlAffoM7zDQ"
        }
    )

async def test_mcp_with_openai():
    """Test MCP with OpenAI model"""
    print("🧪 Testing MCP with OpenAI...")
    
    # Get server parameters
    server_params = get_kavion_server_params()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ MCP server initialized")
            
            # Load MCP tools
            tools = await load_mcp_tools(session)
            print(f"🔧 Loaded {len(tools)} tools: {[tool.name for tool in tools]}")
            
            # Initialize LLM with tools
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key="your-openai-api-key"  # Replace with your actual API key
            )
            llm_with_tools = llm.bind_tools(tools)
            
            # Test query
            response = llm_with_tools.invoke([
                HumanMessage(content="List all my datasets")
            ])
            
            print("🤖 OpenAI Response:")
            print(response.content)
            
            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Tools called: {[call['name'] for call in response.tool_calls]}")

async def test_mcp_with_anthropic():
    """Test MCP with Anthropic Claude model"""
    print("\n🧪 Testing MCP with Anthropic Claude...")
    
    # Get server parameters
    server_params = get_kavion_server_params()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ MCP server initialized")
            
            # Load MCP tools
            tools = await load_mcp_tools(session)
            print(f"🔧 Loaded {len(tools)} tools: {[tool.name for tool in tools]}")
            
            # Initialize LLM with tools
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0,
                api_key="your-anthropic-api-key"  # Replace with your actual API key
            )
            llm_with_tools = llm.bind_tools(tools)
            
            # Test query
            response = llm_with_tools.invoke([
                HumanMessage(content="How many images do I have in the Valero Sim dataset?")
            ])
            
            print("🤖 Anthropic Response:")
            print(response.content)
            
            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Tools called: {[call['name'] for call in response.tool_calls]}")

def test_remote_mcp():
    """Test the remote MCP server via HTTP"""
    print("\n🧪 Testing Remote MCP Server...")
    
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

async def main():
    """Main test function"""
    print("🚀 Starting Kavion MCP Tests for Cursor\n")
    
    # Test 1: Remote MCP Server
    test_remote_mcp()
    
    # Test 2: MCP with OpenAI (uncomment if you have OpenAI API key)
    # await test_mcp_with_openai()
    
    # Test 3: MCP with Anthropic (uncomment if you have Anthropic API key)
    # await test_mcp_with_anthropic()
    
    print("\n✅ All tests completed!")
    print("\n📋 To use in Cursor:")
    print("1. Copy the mcp.json file to your Cursor configuration")
    print("2. Restart Cursor")
    print("3. Ask Cursor: 'List all my datasets' or 'How many images do I have?'")

if __name__ == "__main__":
    asyncio.run(main())