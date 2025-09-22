#!/usr/bin/env python3
"""
Test FastMCP Server using SSE protocol
This script properly tests your FastMCP server using the correct SSE protocol
"""
import requests
import json
import uuid
import time

def test_fastmcp_sse():
    """Test the FastMCP server using SSE protocol"""
    print("🚀 Testing FastMCP Server with SSE Protocol")
    print("=" * 50)
    
    # Test the SSE endpoint
    try:
        print("🔍 Testing SSE endpoint...")
        response = requests.get("http://localhost:8000/sse/", timeout=10, stream=True)
        
        if response.status_code == 200:
            print("✅ FastMCP server is running")
            
            # Read the SSE stream
            session_id = None
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: /messages/?session_id='):
                    session_id = line.split('session_id=')[1]
                    print(f"📡 Session ID: {session_id}")
                    break
                elif line and line.startswith('event:'):
                    print(f"📡 Event: {line}")
                elif line and line.startswith('data:'):
                    print(f"📡 Data: {line}")
                elif line and line.startswith(': ping'):
                    print(f"📡 Ping: {line}")
            
            if session_id:
                print(f"✅ Successfully connected to FastMCP server")
                print(f"📡 Session ID: {session_id}")
                return session_id
            else:
                print("❌ Could not get session ID")
                return None
        else:
            print(f"❌ FastMCP server error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Cannot connect to FastMCP server: {e}")
        return None

def test_fastmcp_tools():
    """Test FastMCP tools directly"""
    print("\n🚀 Testing FastMCP Tools Directly")
    print("=" * 50)
    
    # Test the tools endpoint
    try:
        print("🔍 Testing tools endpoint...")
        response = requests.get("http://localhost:8000/sse/tools/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Tools endpoint is accessible")
            print(f"📊 Response: {response.text[:500]}...")
        else:
            print(f"❌ Tools endpoint error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Tools endpoint error: {e}")

def test_fastmcp_health():
    """Test FastMCP health endpoint"""
    print("\n🚀 Testing FastMCP Health")
    print("=" * 50)
    
    try:
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint is accessible")
            print(f"📊 Response: {response.text}")
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

def main():
    print("🎯 FastMCP Server Test Suite")
    print("=" * 60)
    
    # Test health endpoint
    test_fastmcp_health()
    
    # Test tools endpoint
    test_fastmcp_tools()
    
    # Test SSE endpoint
    session_id = test_fastmcp_sse()
    
    if session_id:
        print(f"\n✅ FastMCP server is working correctly!")
        print(f"📡 Server URL: http://localhost:8000/sse/")
        print(f"📡 Session ID: {session_id}")
        print(f"📡 Tools endpoint: http://localhost:8000/sse/tools/")
        print(f"📡 Health endpoint: http://localhost:8000/health")
    else:
        print(f"\n❌ FastMCP server has issues")

if __name__ == "__main__":
    main()
