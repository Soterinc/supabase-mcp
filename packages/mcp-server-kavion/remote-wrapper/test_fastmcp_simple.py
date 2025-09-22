#!/usr/bin/env python3
"""
Simple test for FastMCP Server
This script tests your FastMCP server without requiring API keys
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
        },
        {
            "name": "get_quick_stats",
            "args": {}
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

def interactive_test():
    """Interactive test mode"""
    print("\n🚀 Interactive FastMCP Test")
    print("=" * 50)
    
    # Get session ID
    try:
        response = requests.get("http://localhost:8000/sse/", timeout=5)
        if response.status_code != 200:
            print("❌ FastMCP server is not running. Please start it with: python3 fastmcp_server.py")
            return
        
        lines = response.text.split('\n')
        session_id = None
        for line in lines:
            if line.startswith('data: /messages/?session_id='):
                session_id = line.split('session_id=')[1]
                break
        
        if not session_id:
            print("❌ Could not get session ID")
            return
            
    except Exception as e:
        print(f"❌ Cannot connect to FastMCP server: {e}")
        return
    
    print("💡 Available commands:")
    print("   - 'list_tables' - List database tables")
    print("   - 'execute_sql <query>' - Execute SQL query")
    print("   - 'search_docs <query>' - Search documentation")
    print("   - 'get_quick_stats' - Get database statistics")
    print("   - 'exit' - Quit")
    
    while True:
        try:
            user_input = input("\n🔍 Command: ").strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                break
            
            if user_input.startswith("execute_sql "):
                query = user_input[12:]  # Remove "execute_sql "
                request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": "execute_sql",
                        "arguments": {"query": query}
                    }
                }
            elif user_input.startswith("search_docs "):
                query = user_input[12:]  # Remove "search_docs "
                request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": "search_docs",
                        "arguments": {"query": query}
                    }
                }
            elif user_input == "list_tables":
                request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": "list_tables",
                        "arguments": {"schemas": ["public"]}
                    }
                }
            elif user_input == "get_quick_stats":
                request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": "get_quick_stats",
                        "arguments": {}
                    }
                }
            else:
                print("❌ Unknown command. Try 'list_tables', 'execute_sql <query>', 'search_docs <query>', or 'get_quick_stats'")
                continue
            
            response = requests.post(
                f"http://localhost:8000/sse/messages/?session_id={session_id}", 
                json=request, 
                timeout=60,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {str(result)[:500]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_fastmcp_server()

if __name__ == "__main__":
    main()