#!/usr/bin/env python3
"""
Working Remote MCP Client
This client properly handles timeouts and shows the AI responses
"""
import requests
import json
import time
import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

def call_remote_mcp_tool(tool_name, tool_args, timeout=120):
    """Call a remote MCP tool with proper timeout handling"""
    try:
        request = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        
        print(f"🔧 Calling {tool_name} with args: {tool_args}")
        response = requests.post(
            "http://localhost:3000/mcp", 
            json=request, 
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"]
            else:
                return result
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout after {timeout}s for {tool_name}")
        return None
    except Exception as e:
        print(f"❌ Error calling {tool_name}: {e}")
        return None

def get_available_tools():
    """Get list of available tools from remote MCP server"""
    try:
        request = {
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            "http://localhost:3000/mcp", 
            json=request, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            return [tool['name'] for tool in tools]
        else:
            print(f"❌ Failed to get tools: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting tools: {e}")
        return []

def process_with_remote_context(user_prompt, conversation_history=None):
    """Process user prompt with remote MCP server"""
    print(f"🤖 Processing: {user_prompt}")
    print("=" * 60)
    
    # Check if remote server is running
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Remote MCP server is running: {health}")
        else:
            print(f"❌ Remote MCP server health check failed: {response.status_code}")
            return "Remote MCP server is not responding properly.", []
    except Exception as e:
        print(f"❌ Cannot connect to remote MCP server: {e}")
        return "Cannot connect to remote MCP server. Please start it with: node working_server.cjs", []
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0, 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Build conversation context
    context_messages = []
    if conversation_history:
        context_messages.extend(conversation_history)
    
    # Add current user message
    context_messages.append(HumanMessage(content=user_prompt))
    
    # Check if this is a SQL-related query
    if not is_sql_related_query(user_prompt):
        # Handle non-SQL queries
        greeting_response = handle_non_sql_query(user_prompt, conversation_history)
        updated_history = context_messages + [AIMessage(content=greeting_response)]
        return greeting_response, updated_history
    
    # Generate SQL query
    sql_generation_prompt = f"""
    You are a SQL expert with access to a database. Based on the conversation history and current question, generate the appropriate SQL query.
    
    Conversation History:
    {format_conversation_history(conversation_history) if conversation_history else "No previous conversation"}
    
    Current question: "{user_prompt}"
    
    Available tables (from previous exploration):
    - datasets (contains: id, name, description, organization_id, owner_id, visibility, provider, storage_path, credentials, created_at, updated_at)
    - images (contains: id, dataset_id, filename, file_size, created_at, updated_at)
    - annotations (contains: id, image_id, category_id, bbox, created_at, updated_at)
    - annotation_categories (contains: id, name, description, created_at, updated_at)
    
    IMPORTANT: 
    - If the user asks for "more" or "additional" items, consider the context from previous queries
    - If they mention a specific dataset from previous conversation, use that dataset
    - Always check the actual schema before making assumptions about column names
    - Generate a valid SQL query that can be executed
    
    Generate a SQL query that answers the user's question. Return ONLY the SQL query, nothing else.
    """
    
    try:
        sql_response = llm.invoke(sql_generation_prompt)
        sql_query = sql_response.content.strip()
        
        # Clean up the SQL query
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql")[1]
        if sql_query.endswith("```"):
            sql_query = sql_query.split("```")[0]
        sql_query = sql_query.strip()
        
        # Validate SQL query
        if not is_valid_sql(sql_query):
            return "I'm sorry, I couldn't generate a valid SQL query for your request. Please try rephrasing your question.", context_messages
        
        print(f"🔧 Generated SQL: {sql_query}")
        
        # Execute the SQL query with longer timeout
        print("🚀 Executing SQL query on remote server...")
        result = call_remote_mcp_tool("execute_sql", {"query": sql_query}, timeout=120)
        
        if result is None:
            return "The SQL query timed out or failed to execute. Please try a simpler query or check the server logs.", context_messages
        
        # Format the result
        print("📝 Formatting result...")
        formatting_prompt = f"""
        Conversation History:
        {format_conversation_history(conversation_history) if conversation_history else "No previous conversation"}
        
        Current question: "{user_prompt}"
        SQL query used: "{sql_query}"
        Query result: "{result}"
        
        Format this result into a clear, human-readable answer. Extract and present the specific information the user requested.
        Consider the conversation context when formatting the response.
        """
        
        formatted_response = llm.invoke(formatting_prompt)
        final_answer = formatted_response.content
        
        # Update conversation history
        updated_history = context_messages + [
            AIMessage(content=final_answer)
        ]
        
        print("✅ Query completed successfully")
        return final_answer, updated_history
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"An error occurred while processing your request: {str(e)}", context_messages

def format_conversation_history(conversation_history):
    """Format conversation history for context"""
    if not conversation_history:
        return "No previous conversation"
    
    formatted = []
    for msg in conversation_history[-6:]:  # Keep last 6 messages for context
        if hasattr(msg, 'content'):
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            formatted.append(f"{role}: {msg.content}")
    
    return "\n".join(formatted)

def is_sql_related_query(user_prompt):
    """Check if the user prompt is related to SQL/database queries"""
    sql_keywords = [
        'list', 'show', 'get', 'find', 'count', 'how many', 'what', 'which', 
        'datasets', 'images', 'data', 'table', 'query', 'select', 'from',
        'where', 'group by', 'order by', 'limit', 'join', 'inner', 'outer'
    ]
    
    prompt_lower = user_prompt.lower()
    
    # Check for greetings and general questions
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in prompt_lower for greeting in greetings):
        return False
    
    # Check for SQL-related keywords
    return any(keyword in prompt_lower for keyword in sql_keywords)

def is_valid_sql(sql_query):
    """Basic validation of SQL query"""
    if not sql_query or len(sql_query.strip()) < 3:
        return False
    
    # Check for common SQL keywords
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
    query_upper = sql_query.upper().strip()
    
    return any(keyword in query_upper for keyword in sql_keywords)

def handle_non_sql_query(user_prompt, conversation_history):
    """Handle non-SQL queries like greetings"""
    prompt_lower = user_prompt.lower()
    
    if any(greeting in prompt_lower for greeting in ['hi', 'hello', 'hey']):
        return "Hello! I'm your thermal and RGB drone imagery analysis assistant. I can help you with questions about your datasets, images, and data. What would you like to know?"
    
    return "I'm here to help you with questions about your thermal and RGB drone imagery data. You can ask me about datasets, images, or any other data-related questions."

def main():
    print("🚀 Starting Working Remote MCP Client...")
    print("🔧 Remote server: http://localhost:3000/mcp")
    
    # Check if remote server is running
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Remote MCP server is not running. Please start it with: node working_server.cjs")
            return
    except Exception as e:
        print(f"❌ Cannot connect to remote MCP server: {e}")
        print("Please start the server with: node working_server.cjs")
        return
    
    # Get available tools
    tools = get_available_tools()
    if tools:
        print(f"🔧 Available tools: {tools}")
    else:
        print("⚠️  Could not retrieve tools list")
    
    print("🤖 Working Remote MCP Client is ready!")
    print("💡 Try commands like:")
    print("   - 'list my datasets'")
    print("   - 'show me thermal images from Valero Sim'")
    print("   - 'analyze the Wacker 2024 dataset'")
    print("   - 'get statistics about my data'")
    print("   - Type 'exit' to quit\n")

    # Maintain conversation history
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n🔍 You: ").strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                break

            response, updated_history = process_with_remote_context(user_input, conversation_history)
            
            # Update conversation history
            conversation_history = updated_history
            
            # Keep only last 10 messages to prevent context overflow
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
            
            print("\n" + "=" * 60)
            print("🤖 RESPONSE:")
            print("=" * 60)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()