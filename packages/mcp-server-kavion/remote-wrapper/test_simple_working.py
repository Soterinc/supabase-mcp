#!/usr/bin/env python3
"""
Simple Working Remote MCP Client
This client tests the remote MCP server with minimal complexity
"""
import requests
import json
import time

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_tools_list():
    """Test tools list endpoint"""
    try:
        request = {
            "method": "tools/list",
            "params": {}
        }
        
        print("🔧 Getting available tools...")
        response = requests.post(
            "http://localhost:3000/mcp", 
            json=request, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"✅ Available tools: {[tool['name'] for tool in tools]}")
            return tools
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Tools list error: {e}")
        return []

def test_execute_sql():
    """Test execute_sql tool"""
    try:
        request = {
            "method": "tools/call",
            "params": {
                "name": "execute_sql",
                "arguments": {"query": "SELECT id, name, description FROM datasets LIMIT 3;"}
            }
        }
        
        print("🧪 Testing execute_sql tool...")
        response = requests.post(
            "http://localhost:3000/mcp", 
            json=request, 
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SQL query successful!")
            print(f"📊 Result: {str(result)[:500]}...")
            return result
        else:
            print(f"❌ SQL query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ SQL query error: {e}")
        return None

def test_list_tables():
    """Test list_tables tool"""
    try:
        request = {
            "method": "tools/call",
            "params": {
                "name": "list_tables",
                "arguments": {"schemas": ["public"]}
            }
        }
        
        print("🧪 Testing list_tables tool...")
        response = requests.post(
            "http://localhost:3000/mcp", 
            json=request, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ List tables successful!")
            print(f"📊 Result: {str(result)[:500]}...")
            return result
        else:
            print(f"❌ List tables failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ List tables error: {e}")
        return None

def interactive_mode():
    """Interactive mode for testing"""
    print("\n🚀 Interactive Remote MCP Test")
    print("=" * 50)
    
    if not test_health():
        return
    
    tools = test_tools_list()
    if not tools:
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
    print("🎯 Simple Working Remote MCP Test")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("❌ Remote MCP server is not running. Please start it with: node working_server.cjs")
        return
    
    # Test tools list
    tools = test_tools_list()
    if not tools:
        print("❌ Could not retrieve tools list")
        return
    
    # Test basic tools
    print("\n🧪 Testing basic tools...")
    test_list_tables()
    test_execute_sql()
    
    # Ask if user wants interactive mode
    try:
        user_input = input("\n🔍 Enter interactive mode? (y/n): ").strip().lower()
        if user_input in {"y", "yes"}:
            interactive_mode()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()