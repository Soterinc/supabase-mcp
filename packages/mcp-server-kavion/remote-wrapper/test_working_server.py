#!/usr/bin/env python3
"""
Test the working remote MCP server
"""
import requests
import json
import time

def test_working_server():
    """Test the working remote MCP server"""
    print("🚀 Testing Working Remote MCP Server")
    print("=" * 50)
    
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

if __name__ == "__main__":
    test_working_server()