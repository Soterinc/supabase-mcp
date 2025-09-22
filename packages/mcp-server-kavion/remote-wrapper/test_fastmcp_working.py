#!/usr/bin/env python3
"""
Working test for FastMCP Server
This script properly handles the SSE protocol
"""
import requests
import json
import uuid
import time

def test_fastmcp_server():
    """Test the FastMCP remote server"""
    print("🚀 Testing FastMCP Remote Server")
    print("=" * 50)
    
    # Get session ID from SSE endpoint
    try:
        print("🔍 Getting session ID from SSE endpoint...")
        response = requests.get("http://localhost:8000/sse/", timeout=10, stream=True)
        
        if response.status_code == 200:
            print("✅ FastMCP server is running")
            
            # Read the first few lines to get session ID
            session_id = None
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: /messages/?session_id='):
                    session_id = line.split('session_id=')[1]
                    break
                if session_id:  # Stop after getting session ID
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
            print(f"📤 Sending request: {json.dumps(request, indent=2)}")
            
            response = requests.post(
                f"http://localhost:8000/sse/messages/?session_id={session_id}", 
                json=request, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {tool['name']} successful!")
                print(f"📊 Result: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ {tool['name']} failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {tool['name']} error: {e}")

def main():
    test_fastmcp_server()

if __name__ == "__main__":
    main()
