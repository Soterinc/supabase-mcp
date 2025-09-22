#!/usr/bin/env python3
"""
Simple Requests Remote MCP Client
This client uses only requests library to test your remote MCP server
"""
import requests
import json
import time
import sys

def test_remote_mcp():
    """Test the remote MCP server with simple requests"""
    print("🚀 Testing Remote MCP Server with Simple Requests")
    print("=" * 60)
    
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
        print("Please start the server with: node working_server.cjs")
        return
    
    # Test MCP tools list
    try:
        tools_request = {
            "method": "tools/list",
            "params": {}
        }
        
        print("\n🔧 Getting available tools...")
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
                
            # Test list_tables tool
            print("\n🧪 Testing list_tables tool...")
            tables_request = {
                "method": "tools/call",
                "params": {
                    "name": "list_tables",
                    "arguments": {"schemas": ["public"]}
                }
            }
            
            response = requests.post(
                "http://localhost:3000/mcp", 
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
                
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_test():
    """Interactive test mode"""
    print("\n🚀 Interactive Remote MCP Test")
    print("=" * 50)
    
    # Check if remote server is running
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Remote MCP server is not running. Please start it with: node working_server.cjs")
            return
    except Exception as e:
        print(f"❌ Cannot connect to remote MCP server: {e}")
        return
    
    print("\n💡 Available commands:")
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
                "http://localhost:3000/mcp", 
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
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_remote_mcp()

if __name__ == "__main__":
    main()