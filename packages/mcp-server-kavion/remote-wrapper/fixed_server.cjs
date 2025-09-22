const http = require('http');
const { spawn } = require('child_process');
const url = require('url');
const cors = require('cors');
const express = require('express');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const MCP_SERVER_PATH = "/home/behnam/git/KavApps/kavion-v0/supabase-mcp/packages/mcp-server-kavion/dist/transports/stdio.js";

let mcpProcess = null;
let mcpReady = false;
let pendingRequests = new Map();
let requestId = 0;

// Initialize MCP Server
function startMCPServer() {
  console.log('🚀 Starting Kavion MCP Server...');
  
  mcpProcess = spawn('node', [MCP_SERVER_PATH, '--read-only', '--features=database,docs', '--user-email=behnammoradi026@gmail.com', '--user-password=Behnam1993!'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: {
      ...process.env,
      SUPABASE_URL: process.env.SUPABASE_URL || "https://vwovgsttefakrjcaytin.supabase.co",
      SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3b3Znc3R0ZWZha3JqY2F5dGluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NTgxNDUsImV4cCI6MjA2MzMzNDE0NX0.3ZzaKTX6PS68f8-VPkwqr5ng4-Iwu5_aNlAffoM7zDQ"
    }
  });

  let buffer = '';
  
  mcpProcess.stdout.on('data', (data) => {
    const output = data.toString();
    buffer += output;
    
    // Check for server ready message
    if (output.includes('Server connected and ready!')) {
      mcpReady = true;
      console.log('✅ MCP Server is ready');
    }
    
    // Process JSON-RPC responses
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line);
          if (response.id && pendingRequests.has(response.id)) {
            const { resolve, reject } = pendingRequests.get(response.id);
            pendingRequests.delete(response.id);
            resolve(response);
          }
        } catch (e) {
          // Not a JSON response, might be server log
          console.log('MCP Server:', line);
        }
      }
    }
  });

  mcpProcess.stderr.on('data', (data) => {
    console.error('MCP Server Error:', data.toString());
  });

  mcpProcess.on('close', (code) => {
    console.log(`MCP Server process exited with code ${code}`);
    mcpReady = false;
    // Restart after 5 seconds
    setTimeout(() => {
      console.log('🔄 Restarting MCP Server...');
      startMCPServer();
    }, 5000);
  });

  mcpProcess.on('error', (err) => {
    console.error('Failed to start MCP Server:', err);
    mcpReady = false;
  });
}

// Start the MCP server
startMCPServer();

// Middleware for CORS
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    mcpServerReady: mcpReady, 
    timestamp: new Date().toISOString() 
  });
});

// HTTP endpoint for MCP JSON-RPC requests
app.post('/mcp', async (req, res) => {
  if (!mcpReady) {
    return res.status(503).json({ error: 'MCP server not ready' });
  }

  const { method, params, id } = req.body;

  if (!method) {
    return res.status(400).json({ error: 'Method is required' });
  }

  // Generate unique request ID
  const requestId = Date.now() + Math.random();
  
  // Forward request to MCP server via stdio
  const request = JSON.stringify({ jsonrpc: '2.0', id: requestId, method, params }) + '\n';
  
  try {
    // Create promise for response
    const responsePromise = new Promise((resolve, reject) => {
      pendingRequests.set(requestId, { resolve, reject });
      
      // Timeout after 60 seconds
      setTimeout(() => {
        if (pendingRequests.has(requestId)) {
          pendingRequests.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 60000);
    });

    // Write to MCP server's stdin
    mcpProcess.stdin.write(request);
    
    // Wait for response
    const response = await responsePromise;
    res.json(response);
    
  } catch (error) {
    console.error('Error forwarding to MCP server:', error);
    res.status(500).json({ error: 'Failed to communicate with MCP server: ' + error.message });
  }
});

// Start HTTP server
const httpServer = http.createServer(app);
httpServer.listen(PORT, () => {
  console.log(`🚀 Kavion MCP Remote Server running on port ${PORT}`);
  console.log(`📡 HTTP endpoint: http://localhost:${PORT}/mcp`);
  console.log(`❤️  Health check: http://localhost:${PORT}/health`);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('🛑 Shutting down gracefully...');
  if (mcpProcess) {
    mcpProcess.kill(); // Terminate the child MCP process
  }
  httpServer.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});