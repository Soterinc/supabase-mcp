#!/usr/bin/env python3
"""
LangChain OpenAI Remote MCP Client - Final Version
This client uses LangChain with OpenAI and your remote MCP server
"""
import os
import sys
from langchain_openai import ChatOpenAI

def test_openai_remote_mcp():
    """Test OpenAI with remote MCP server"""
    print("🚀 Testing OpenAI with Remote MCP Server")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please set it to test OpenAI.")
        print("   export OPENAI_API_KEY='your-key-here'")
        return
    
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
            "server_url": "http://localhost:3000/mcp",
            "require_approval": "never",
        }
    ])
    
    # Test query
    query = "List all my datasets"
    print(f"🔍 Query: {query}")
    
    try:
        response = llm_with_tools.invoke(query)
        print(f"✅ Response: {response.content}")
        
        # Check for tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🔧 Tool calls: {response.tool_calls}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_simple_remote_call():
    """Test simple remote MCP call without LangChain"""
    print("\n🚀 Testing Simple Remote MCP Call")
    print("=" * 50)
    
    import requests
    import json
    
    # Test health check
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to remote server: {e}")
        return
    
    # Test MCP tools list
    try:
        tools_request = {
            "method": "tools/list",
            "params": {}
        }
        
        print("🔧 Getting available tools...")
        response = requests.post(
            "http://localhost:3000/mcp", 
            json=tools_request, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"✅ Available tools: {[tool['name'] for tool in tools]}")
            
            # Test execute_sql tool
            print("\n🧪 Testing execute_sql tool...")
            sql_request = {
                "method": "tools/call",
                "params": {
                    "name": "execute_sql",
                    "arguments": {"query": "SELECT id, name, description FROM datasets LIMIT 3;"}
                }
            }
            
            response = requests.post(
                "http://localhost:3000/mcp", 
                json=sql_request, 
                timeout=60,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SQL query successful!")
                print(f"📊 Result: {str(result)[:500]}...")
            else:
                print(f"❌ SQL query failed: {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🎯 LangChain OpenAI Remote MCP Test")
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
    
    # Test simple remote call first
    test_simple_remote_call()
    
    # Test OpenAI if API key is available
    if os.getenv("OPENAI_API_KEY"):
        test_openai_remote_mcp()
    else:
        print("\n⚠️  OPENAI_API_KEY not set, skipping OpenAI test")
        print("To test OpenAI, set your API key: export OPENAI_API_KEY='your-key-here'")

if __name__ == "__main__":
    main()