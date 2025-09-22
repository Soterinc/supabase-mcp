#!/usr/bin/env python3
"""
FastMCP Remote Server for Kavion MCP
This creates a proper remote MCP server using FastMCP
"""
import os
import asyncio
import subprocess
import json
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

# Global MCP process
mcp_process = None

def start_mcp_server():
    """Start the local MCP server process"""
    global mcp_process
    try:
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
        return True
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        return False

def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call a tool on the local MCP server"""
    global mcp_process
    
    if not mcp_process:
        if not start_mcp_server():
            return "Error: Could not start MCP server"
    
    try:
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request to MCP server
        mcp_process.stdin.write(json.dumps(request) + "\n")
        mcp_process.stdin.flush()
        
        # Read response
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

if __name__ == "__main__":
    import asyncio
    
    # Start the MCP server
    if start_mcp_server():
        print("✅ Local MCP server started")
    else:
        print("❌ Failed to start local MCP server")
        exit(1)
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting FastMCP Remote Server on port {port}")
    print(f"📡 Server URL: http://localhost:{port}/mcp")
    print(f"❤️  Health check: http://localhost:{port}/health")
    
    # Run the FastMCP server
    asyncio.run(
        mcp.run_sse_async(
            host="0.0.0.0",  # Allow external connections
            port=port,
            log_level="info"
        )
    )
