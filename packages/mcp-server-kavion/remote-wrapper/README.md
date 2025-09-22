# Kavion MCP Remote Server

A simple HTTP wrapper for the Kavion MCP server that enables remote access to your MCP tools over the network.

## Quick Start

### 1. Build the MCP Server

First, make sure the MCP server is built:

```bash
cd ..
npm run build
```

### 2. Start the Remote Server

```bash
node simple-server.js
```

The server will be available at:
- **HTTP API**: http://localhost:3000/mcp
- **Health Check**: http://localhost:3000/health

### 3. Test the Server

```bash
node test-simple.js
```

## Usage Examples

### HTTP API

```bash
# Health check
curl http://localhost:3000/health

# List available tools
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'

# Execute a tool
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {"query": "SELECT * FROM datasets LIMIT 5;"}
    }
  }'
```

### LangChain Integration

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools([
    {
        "type": "mcp",
        "server_label": "kavion",
        "server_url": "http://localhost:3000/mcp",
        "require_approval": "never",
    }
])

response = llm_with_tools.invoke("List all my datasets")
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3000` |
| `SUPABASE_URL` | Supabase URL | Required |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Required |

## API Endpoints

### POST /mcp

Execute MCP tools via HTTP.

**Request Body:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {...}
  }
}
```

**Response:**
```json
{
  "result": {
    "content": [...],
    "isError": false
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "mcpServerReady": true,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Features

- **HTTP API**: RESTful endpoints for MCP tool execution
- **Process Management**: Automatic MCP server lifecycle management
- **Health Checks**: Built-in health monitoring
- **CORS Support**: Cross-origin requests enabled
- **Error Handling**: Graceful error handling and logging

## Troubleshooting

### MCP Server Not Starting

1. Check if the MCP server is built: `npm run build`
2. Verify environment variables are set
3. Check the console output for errors

### Connection Issues

1. Verify the server is running: `curl http://localhost:3000/health`
2. Check firewall settings
3. Ensure port 3000 is available

## License

MIT