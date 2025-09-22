#!/usr/bin/env python3
"""
Setup script for Cursor MCP integration
This script helps you configure Cursor to use your Kavion MCP server
"""

import json
import os
import shutil
from pathlib import Path

def setup_cursor_mcp():
    """Setup Cursor MCP configuration"""
    
    # MCP configuration for direct stdio connection
    mcp_config = {
        "mcpServers": {
            "kavion-thermal-jwt": {
                "command": "node",
                "args": [
                    "/home/behnam/git/KavApps/kavion-v0/supabase-mcp/packages/mcp-server-kavion/dist/transports/stdio.js",
                    "--read-only",
                    "--features=database,docs",
                    "--user-email=behnammoradi026@gmail.com",
                    "--user-password=Behnam1993!"
                ],
                "env": {
                    "SUPABASE_URL": "https://vwovgsttefakrjcaytin.supabase.co",
                    "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3b3Znc3R0ZWZha3JqY2F5dGluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NTgxNDUsImV4cCI6MjA2MzMzNDE0NX0.3ZzaKTX6PS68f8-VPkwqr5ng4-Iwu5_aNlAffoM7zDQ"
                }
            }
        }
    }
    
    # Possible Cursor configuration locations
    cursor_config_paths = [
        Path.home() / ".cursor" / "mcp.json",
        Path.home() / ".config" / "cursor" / "mcp.json",
        Path.home() / "Library" / "Application Support" / "Cursor" / "mcp.json",  # macOS
        Path.home() / "AppData" / "Roaming" / "Cursor" / "mcp.json",  # Windows
    ]
    
    print("🚀 Setting up Cursor MCP configuration...")
    
    # Find the correct Cursor config directory
    config_dir = None
    for path in cursor_config_paths:
        if path.parent.exists():
            config_dir = path.parent
            break
    
    if not config_dir:
        # Create default config directory
        config_dir = Path.home() / ".cursor"
        config_dir.mkdir(exist_ok=True)
        print(f"📁 Created config directory: {config_dir}")
    
    config_file = config_dir / "mcp.json"
    
    # Write the configuration
    with open(config_file, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"✅ MCP configuration written to: {config_file}")
    
    # Also create a local copy
    local_config = Path("mcp.json")
    with open(local_config, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"✅ Local copy created: {local_config}")
    
    return config_file

def test_mcp_server():
    """Test if the MCP server is working"""
    print("\n🧪 Testing MCP server...")
    
    # Check if the MCP server file exists
    mcp_server_path = Path("/home/behnam/git/KavApps/kavion-v0/supabase-mcp/packages/mcp-server-kavion/dist/transports/stdio.js")
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found at: {mcp_server_path}")
        print("Please run 'npm run build' in the mcp-server-kavion directory")
        return False
    
    print(f"✅ MCP server found at: {mcp_server_path}")
    return True

def main():
    """Main setup function"""
    print("🎯 Kavion MCP Cursor Setup")
    print("=" * 50)
    
    # Test MCP server
    if not test_mcp_server():
        return
    
    # Setup Cursor configuration
    config_file = setup_cursor_mcp()
    
    print("\n📋 Next Steps:")
    print("1. Restart Cursor")
    print("2. Open Cursor's AI chat")
    print("3. Try these commands:")
    print("   - 'List all my datasets'")
    print("   - 'How many images do I have in Valero Sim?'")
    print("   - 'Show me the database schema'")
    print("   - 'Search for thermal imaging documentation'")
    
    print(f"\n🔧 Configuration file: {config_file}")
    print("💡 If Cursor doesn't pick up the configuration, try:")
    print("   - Restarting Cursor completely")
    print("   - Checking Cursor's settings for MCP configuration")
    print("   - Looking for MCP-related settings in Cursor's preferences")

if __name__ == "__main__":
    main()