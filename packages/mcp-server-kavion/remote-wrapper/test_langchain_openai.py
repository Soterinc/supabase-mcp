#!/usr/bin/env python3
"""
LangChain OpenAI Remote MCP Client
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
            
            # Test a simple tool call
            if tools:
                tool_name = "list_tables"
                print(f"🧪 Testing tool: {tool_name}")
                
                tool_request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {"schemas": ["public"]}
                    }
                }
                
                response = requests.post(
                    "http://localhost:3000/mcp", 
                    json=tool_request, 
                    timeout=30,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Tool call successful: {str(result)[:200]}...")
                else:
                    print(f"❌ Tool call failed: {response.status_code}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            
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
            print("❌ Remote MCP server is not running. Please start it with: node simple-server.cjs")
            return
    except Exception as e:
        print(f"❌ Cannot connect to remote MCP server: {e}")
        print("Please start the server with: node simple-server.cjs")
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