#!/usr/bin/env python3
"""
Fixed FastMCP Remote Server for Kavion MCP with Proper Ready State Management
This creates a proper remote MCP server using FastMCP with proper initialization timing
"""
import os
import asyncio
import subprocess
import json
import time
import threading
from fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP(
    name="Kavion Thermal/RGB MCP Server",
    instructions="A remote MCP server for thermal and RGB drone imagery analysis. Provides access to datasets, images, and data analysis tools."
)

# MCP server configuration
MCP_SERVER_PATH = "/home/behnam/git/KavApps/kavion-v0/supabase-mcp/packages/mcp-server-kavion/dist/transports/stdio.js"
SUPABASE_URL = "https://vwovgsttefakrjcaytin.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3b3Znc3R0ZWZha3JqY2F5dGluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NTgxNDUsImV4cCI6MjA2MzMzNDE0NX0.3ZzaKTX6PS68f8-VPkwqr5ng4-Iwu5_aNlAffoM7zDQ"

# Global MCP process and state
mcp_process = None
mcp_initialized = False
mcp_ready_event = threading.Event()

def start_mcp_server():
    """Start the local MCP server process and wait for initialization"""
    global mcp_process, mcp_initialized, mcp_ready_event
    
    try:
        print("🚀 Starting MCP server process...")
        mcp_process = subprocess.Popen([
            'node', MCP_SERVER_PATH,
            '--read-only',
            '--features=database,docs',
            '--user-email=behnammoradi026@gmail.com',
            '--user-password=Behnam1993!'
        ], 
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={
            **os.environ,
            'SUPABASE_URL': SUPABASE_URL,
            'SUPABASE_ANON_KEY': SUPABASE_ANON_KEY
        })
        
        # Wait for MCP server to be ready
        print("⏳ Waiting for MCP server initialization...")
        time.sleep(2)  # Give the server time to start
        
        # Try to initialize the MCP connection
        try:
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "fastmcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            mcp_process.stdin.write(json.dumps(init_request) + "\n")
            mcp_process.stdin.flush()
            
            # Read initialization response - skip non-JSON lines
            max_attempts = 10
            for attempt in range(max_attempts):
                response_line = mcp_process.stdout.readline()
                if response_line:
                    line = response_line.strip()
                    print(f"🔍 Raw response (attempt {attempt + 1}): {line}")
                    
                    # Skip non-JSON lines (startup messages)
                    if line.startswith('🚀') or line.startswith('✅') or line.startswith('❌'):
                        continue
                    
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            print("✅ MCP server initialized successfully")
                            mcp_initialized = True
                            mcp_ready_event.set()  # Signal that MCP is ready
                            return True
                        else:
                            print(f"❌ MCP initialization failed: {response}")
                            return False
                    except json.JSONDecodeError:
                        # Not JSON, continue to next line
                        continue
                else:
                    print("❌ No response from MCP server during initialization")
                    return False
            
            print("❌ Max attempts reached, no valid JSON response")
            return False
                
        except Exception as e:
            print(f"❌ Error during MCP initialization: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        return False

def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call a tool on the local MCP server"""
    global mcp_process, mcp_initialized, mcp_ready_event
    
    # Wait for MCP server to be ready
    if not mcp_ready_event.is_set():
        print("⏳ Waiting for MCP server to be ready...")
        if not mcp_ready_event.wait(timeout=30):  # Wait up to 30 seconds
            return "Error: MCP server not ready after 30 seconds"
    
    if not mcp_process or not mcp_initialized:
        if not start_mcp_server():
            return "Error: Could not start or initialize MCP server"
    
    try:
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request to MCP server
        mcp_process.stdin.write(json.dumps(request) + "\n")
        mcp_process.stdin.flush()
        
        # Read response with timeout
        import select
        import sys
        
        # Use select to check if data is available (Unix only)
        if hasattr(select, 'select'):
            ready, _, _ = select.select([mcp_process.stdout], [], [], 10)  # 10 second timeout
            if ready:
                response_line = mcp_process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        return str(response["result"])
                    elif "error" in response:
                        return f"Error: {response['error']}"
            else:
                return "Error: Timeout waiting for MCP server response"
        else:
            # Fallback for systems without select
            response_line = mcp_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    return str(response["result"])
                elif "error" in response:
                    return f"Error: {response['error']}"
        
        return "No response from MCP server"
        
    except Exception as e:
        return f"Error calling MCP tool: {e}"

@mcp.tool()
def execute_sql(query: str) -> str:
    """
    Execute a SQL query on the database.
    
    Args:
        query: The SQL query to execute
        
    Returns:
        The result of the SQL query
    """
    return call_mcp_tool("execute_sql", {"query": query})

@mcp.tool()
def list_tables(schemas: list = None) -> str:
    """
    List tables in the database.
    
    Args:
        schemas: List of schema names to search (defaults to ['public'])
        
    Returns:
        List of tables in the specified schemas
    """
    if schemas is None:
        schemas = ["public"]
    return call_mcp_tool("list_tables", {"schemas": schemas})

@mcp.tool()
def search_docs(query: str) -> str:
    """
    Search the documentation.
    
    Args:
        query: The search query
        
    Returns:
        Relevant documentation content
    """
    return call_mcp_tool("search_docs", {"query": query})

@mcp.tool()
def get_quick_stats() -> str:
    """
    Get quick statistics about the database.
    
    Returns:
        Quick statistics about the database
    """
    return call_mcp_tool("get_quick_stats", {})

@mcp.tool()
def list_extensions() -> str:
    """
    List database extensions.
    
    Returns:
        List of database extensions
    """
    return call_mcp_tool("list_extensions", {})

@mcp.tool()
def list_migrations() -> str:
    """
    List database migrations.
    
    Returns:
        List of database migrations
    """
    return call_mcp_tool("list_migrations", {})

@mcp.tool()
def apply_migration(name: str, query: str) -> str:
    """
    Apply a database migration.
    
    Args:
        name: The name of the migration
        query: The SQL query for the migration
        
    Returns:
        Result of applying the migration
    """
    return call_mcp_tool("apply_migration", {"name": name, "query": query})

async def start_server_with_ready_state():
    """Start the server only after MCP is ready"""
    # Start the MCP server first
    if start_mcp_server():
        print("✅ Local MCP server started and initialized")
    else:
        print("❌ Failed to start local MCP server")
        print("🛑 Exiting - cannot start FastMCP server without working MCP backend")
        return False
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting FastMCP Remote Server on port {port}")
    print(f"📡 Server URL: http://localhost:{port}/sse")
    print(f"❤️  Health check: http://localhost:{port}/health")
    
    # Run the FastMCP server
    await mcp.run_sse_async(
        host="0.0.0.0",  # Allow external connections
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    import asyncio
    import sys
    
    # Run the server with proper ready state management
    try:
        result = asyncio.run(start_server_with_ready_state())
        if result is False:
            print("❌ Server startup failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
