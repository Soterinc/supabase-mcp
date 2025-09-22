#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import express from 'express';
import cors from 'cors';
import { createKavionMcpServer } from '../server.js';

const app = express();
app.use(cors());
app.use(express.json());

// Parse command line arguments
const args = process.argv.slice(2);
let apiUrl = '';
let apiKey = '';
let userEmail = '';
let userPassword = '';

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--apiUrl':
      apiUrl = args[++i];
      break;
    case '--apiKey':
      apiKey = args[++i];
      break;
    case '--userEmail':
      userEmail = args[++i];
      break;
    case '--userPassword':
      userPassword = args[++i];
      break;
    case '--help':
      console.log(`
Usage: node http.js [options]

Options:
  --apiUrl <url>        Supabase API URL (required)
  --apiKey <key>        Supabase API key (required)
  --userEmail <email>   User email for authentication (required)
  --userPassword <pass> User password for authentication (required)
  --port <port>         HTTP server port (default: 3000)
  --help                Show this help message

Example:
  node http.js --apiUrl https://your-project.supabase.co --apiKey your-key --userEmail user@example.com --userPassword password
      `);
      process.exit(0);
      break;
  }
}

if (!apiUrl || !apiKey || !userEmail || !userPassword) {
  console.error('❌ Error: Missing required arguments');
  console.error('Use --help for usage information');
  process.exit(1);
}

const port = process.env.PORT || 3000;

// Create the MCP server
const server = new Server(
  {
    name: 'kavion-http-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Create Kavion MCP server instance
const kavionServer = createKavionMcpServer({
  supabaseUrl: apiUrl,
  supabaseKey: apiKey,
  userEmail,
  userPassword,
});

// Set up tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'execute_sql',
        description: 'Execute SQL queries on the database',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'SQL query to execute',
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'list_tables',
        description: 'List tables in the database',
        inputSchema: {
          type: 'object',
          properties: {
            schemas: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of schemas to query',
            },
          },
        },
      },
      {
        name: 'search_docs',
        description: 'Search documentation',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query',
            },
          },
          required: ['query'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'execute_sql':
        return await kavionServer.executeSql(args.query);
      case 'list_tables':
        return await kavionServer.listTables(args.schemas || ['public']);
      case 'search_docs':
        return await kavionServer.searchDocs(args.query);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    throw new Error(`Tool execution failed: ${error.message}`);
  }
});

// HTTP endpoints
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    server: 'kavion-http-mcp-server',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

app.post('/mcp', async (req, res) => {
  try {
    const { method, params } = req.body;
    
    if (method === 'tools/list') {
      const result = await server.request({
        method: 'tools/list',
        params: {},
      });
      res.json({ result });
    } else if (method === 'tools/call') {
      const result = await server.request({
        method: 'tools/call',
        params,
      });
      res.json({ result });
    } else {
      res.status(400).json({ error: 'Unknown method' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start the HTTP server
app.listen(port, () => {
  console.log(`🚀 Kavion HTTP MCP Server running on port ${port}`);
  console.log(`📡 HTTP endpoint: http://localhost:${port}/mcp`);
  console.log(`❤️  Health check: http://localhost:${port}/health`);
  console.log(`🔧 Connected to: ${apiUrl}`);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});