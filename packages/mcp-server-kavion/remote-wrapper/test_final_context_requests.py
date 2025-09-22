#!/usr/bin/env python3
"""
Remote version of final_context_client.py using requests
This client connects to the remote HTTP MCP server instead of local stdio
"""
import os
import sys
import json
import requests
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Remote MCP server configuration
REMOTE_MCP_URL = "http://localhost:3000/mcp"
REMOTE_MCP_HEALTH_URL = "http://localhost:3000/health"

def check_remote_server():
    """Check if the remote MCP server is running"""
    try:
        response = requests.get(REMOTE_MCP_HEALTH_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Remote MCP server is running: {data}")
            return True
        else:
            print(f"❌ Remote MCP server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to remote MCP server: {e}")
        return False

def call_remote_mcp_tool(tool_name, tool_args):
    """Call a tool on the remote MCP server"""
    try:
        # Call the specific tool
        tool_request = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        
        response = requests.post(
            REMOTE_MCP_URL, 
            json=tool_request, 
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Tool call failed: {response.status_code}")
        
        result = response.json()
        return result.get('result', {}).get('content', [{}])[0].get('text', str(result))
        
    except Exception as e:
        raise Exception(f"Remote MCP call failed: {str(e)}")

def process_with_remote_context(user_prompt, conversation_history=None, max_iterations=3):
    """
    Process a user prompt using the remote MCP server
    """
    print(f"🤖 Processing: {user_prompt}")
    print("=" * 60)
    
    # Check if remote server is running
    if not check_remote_server():
        return "❌ Remote MCP server is not running. Please start it with: node simple-server.cjs", []
    
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
    
    # Step 1: Check if this is a SQL-related query
    if not is_sql_related_query(user_prompt):
        # Handle non-SQL queries (greetings, general questions)
        greeting_response = handle_non_sql_query(user_prompt, conversation_history)
        updated_history = context_messages + [AIMessage(content=greeting_response)]
        return greeting_response, updated_history
    
    # Step 2: Generate SQL query with full conversation context
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
        
        # Clean up the SQL query (remove markdown formatting if present)
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql")[1]
        if sql_query.endswith("```"):
            sql_query = sql_query.split("```")[0]
        sql_query = sql_query.strip()
        
        # Validate SQL query
        if not is_valid_sql(sql_query):
            return "I'm sorry, I couldn't generate a valid SQL query for your request. Please try rephrasing your question.", context_messages
        
        print(f"🔧 Generated SQL: {sql_query}")
        
        # Step 3: Execute the SQL query on remote server
        print("🚀 Executing SQL query on remote server...")
        result = call_remote_mcp_tool("execute_sql", {"query": sql_query})
        
        # Step 4: Format the result with context
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
        # Fallback to MCP tools approach
        return process_with_remote_mcp_tools(user_prompt, conversation_history, max_iterations)

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

def process_with_remote_mcp_tools(user_prompt, conversation_history=None, max_iterations=3):
    """
    Fallback processing using remote MCP tools directly.
    """
    print("🔄 Falling back to remote MCP tools approach...")
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0, 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Simple prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant for thermal and RGB drone imagery analysis. Use the available tools to help answer questions about datasets, images, and data. When you encounter errors, investigate the database schema to understand the correct approach. CRITICAL: When you retrieve data from tools, you MUST extract and present the actual information the user requested."),
        MessagesPlaceholder("messages")
    ])
    
    # Initialize conversation
    if conversation_history:
        messages = conversation_history + [HumanMessage(content=user_prompt)]
    else:
        messages = [HumanMessage(content=user_prompt)]
    
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"🔄 Iteration {iteration}")
        
        # Get AI response
        response = llm.invoke(messages)
        messages.append(response)
        
        # Check if AI wants to use tools (simplified approach)
        if "execute_sql" in response.content or "list_tables" in response.content or "search_docs" in response.content:
            print(f"🔧 AI wants to use tools")
            
            # Try to extract tool name and arguments from response
            tool_name = None
            tool_args = {}
            
            if "execute_sql" in response.content:
                tool_name = "execute_sql"
                # Extract SQL query from response
                if "SELECT" in response.content:
                    sql_start = response.content.find("SELECT")
                    sql_end = response.content.find(";", sql_start)
                    if sql_end == -1:
                        sql_end = len(response.content)
                    sql_query = response.content[sql_start:sql_end].strip()
                    tool_args = {"query": sql_query}
            
            elif "list_tables" in response.content:
                tool_name = "list_tables"
                tool_args = {"schemas": ["public"]}
            
            elif "search_docs" in response.content:
                tool_name = "search_docs"
                tool_args = {"query": user_prompt}
            
            if tool_name:
                print(f"  📋 Calling tool: {tool_name}")
                print(f"  📋 Arguments: {tool_args}")
                
                try:
                    # Execute the tool on remote server
                    tool_result = call_remote_mcp_tool(tool_name, tool_args)
                    print(f"  ✅ Tool result: {str(tool_result)[:200]}...")
                    
                    # Add tool result to messages
                    tool_message = ToolMessage(
                        content=str(tool_result),
                        tool_call_id=f"tool_{iteration}"
                    )
                    messages.append(tool_message)
                    
                except Exception as e:
                    print(f"  ❌ Tool error: {e}")
                    tool_message = ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=f"tool_{iteration}"
                    )
                    messages.append(tool_message)
        else:
            # No more tool calls, return the response
            print("✅ AI response received")
            final_response = response.content if hasattr(response, 'content') else str(response)
            return final_response, messages
    
    # Return the final AI message and updated conversation history
    final_response = messages[-1].content if messages else "No response generated"
    return final_response, messages

def main():
    # Check if a prompt was provided as command line argument
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"🚀 Processing prompt: {user_prompt}")
        single_mode = True
    else:
        single_mode = False
    
    print("🚀 Starting Remote MCP Client...")
    print(f"🔧 Remote server: {REMOTE_MCP_URL}")
    
    if single_mode:
        print("🤖 Processing single prompt with remote MCP server...")
        try:
            response, _ = process_with_remote_context(user_prompt)
            print("\n" + "=" * 60)
            print("🤖 FINAL RESPONSE:")
            print("=" * 60)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("🤖 Remote MCP Client is ready!")
        print("💡 Try commands like:")
        print("   - 'list my datasets'")
        print("   - 'show me thermal images from Valero Sim'")
        print("   - 'analyze the Wacker 2024 dataset'")
        print("   - 'get statistics about my data'")
        print("   - Type 'exit' to quit\n")

        # Maintain conversation history
        conversation_history = []
        
        while True:
            user_input = input("\n🔍 You: ").strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                break

            try:
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
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()