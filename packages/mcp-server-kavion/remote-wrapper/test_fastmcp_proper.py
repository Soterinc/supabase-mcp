#!/usr/bin/env python3
"""
Proper test for FastMCP Remote Server using the correct protocol
"""
import requests
import json
import time
import uuid

def test_fastmcp_server():
    """Test the FastMCP remote server using proper protocol"""
    print("🚀 Testing FastMCP Remote Server")
    print("=" * 50)
    
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
    
    # Test MCP tools via HTTP
    print("\n🔧 Testing MCP tools...")
    
    # Test execute_sql
    try:
        sql_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "execute_sql",
                "arguments": {"query": "SELECT id, name, description FROM datasets LIMIT 3;"}
            }
        }
        
        print("🧪 Testing execute_sql tool...")
        response = requests.post(
            f"http://localhost:8000/sse/messages/?session_id={session_id}", 
            json=sql_request, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SQL query successful!")
            print(f"📊 Result: {str(result)[:500]}...")
        else:
            print(f"❌ SQL query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ SQL query error: {e}")
    
    # Test list_tables
    try:
        tables_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "list_tables",
                "arguments": {"schemas": ["public"]}
            }
        }
        
        print("\n🧪 Testing list_tables tool...")
        response = requests.post(
            f"http://localhost:8000/sse/messages/?session_id={session_id}", 
            json=tables_request, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ List tables successful!")
            print(f"📊 Result: {str(result)[:500]}...")
        else:
            print(f"❌ List tables failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ List tables error: {e}")

def main():
    test_fastmcp_server()

if __name__ == "__main__":
    main()
