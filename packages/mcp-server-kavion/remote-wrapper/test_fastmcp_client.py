#!/usr/bin/env python3
"""
Test client for FastMCP Remote Server
"""
import requests
import json
import time

def test_fastmcp_server():
    """Test the FastMCP remote server"""
    print("🚀 Testing FastMCP Remote Server")
    print("=" * 50)
    
    # Test SSE endpoint
    try:
        response = requests.get("http://localhost:8000/sse/", timeout=5)
        if response.status_code == 200:
            print("✅ FastMCP server is running")
            print(f"📡 SSE endpoint: http://localhost:8000/sse/")
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
            "method": "tools/call",
            "params": {
                "name": "execute_sql",
                "arguments": {"query": "SELECT id, name, description FROM datasets LIMIT 3;"}
            }
        }
        
        print("🧪 Testing execute_sql tool...")
        response = requests.post(
            "http://localhost:8000/sse/messages/", 
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
            "method": "tools/call",
            "params": {
                "name": "list_tables",
                "arguments": {"schemas": ["public"]}
            }
        }
        
        print("\n🧪 Testing list_tables tool...")
        response = requests.post(
            "http://localhost:8000/sse/messages/", 
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

def interactive_test():
    """Interactive test mode"""
    print("\n🚀 Interactive FastMCP Test")
    print("=" * 50)
    
    print("💡 Available commands:")
    print("   - 'list_tables' - List database tables")
    print("   - 'execute_sql <query>' - Execute SQL query")
    print("   - 'search_docs <query>' - Search documentation")
    print("   - 'exit' - Quit")
    
    while True:
        try:
            user_input = input("\n🔍 Command: ").strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                break
            
            if user_input.startswith("execute_sql "):
                query = user_input[12:]  # Remove "execute_sql "
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": "execute_sql",
                        "arguments": {"query": query}
                    }
                }
            elif user_input.startswith("search_docs "):
                query = user_input[12:]  # Remove "search_docs "
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": "search_docs",
                        "arguments": {"query": query}
                    }
                }
            elif user_input == "list_tables":
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": "list_tables",
                        "arguments": {"schemas": ["public"]}
                    }
                }
            else:
                print("❌ Unknown command. Try 'list_tables', 'execute_sql <query>', or 'search_docs <query>'")
                continue
            
            response = requests.post(
                "http://localhost:8000/sse/messages/", 
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
