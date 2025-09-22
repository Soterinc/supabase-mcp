#!/usr/bin/env node

const http = require('http');
const { spawn } = require('child_process');
const { join } = require('path');

// Configuration
const PORT = process.env.PORT || 3000;
const MCP_SERVER_PATH = join(__dirname, '..', 'dist', 'transports', 'stdio.js');

// MCP Server Process Management
let mcpProcess = null;
let mcpProcessReady = false;

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

  mcpProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log('MCP Server:', output);
    
    // Check if server is ready
    if (output.includes('initialized') || output.includes('ready')) {
      mcpProcessReady = true;
      console.log('✅ MCP Server is ready');
    }
    
    // Handle MCP server responses for HTTP requests
    const lines = output.split('\n');
    lines.forEach(line => {
      if (line.trim() && line.startsWith('{')) {
        mcpHandler.handleResponse(line);
      }
    });
  });

  mcpProcess.stderr.on('data', (data) => {
    console.error('MCP Server Error:', data.toString());
  });

  mcpProcess.on('close', (code) => {
    console.log(`MCP Server process exited with code ${code}`);
    mcpProcessReady = false;
    
    // Restart after 5 seconds
    setTimeout(() => {
      console.log('🔄 Restarting MCP Server...');
      startMCPServer();
    }, 5000);
  });

  mcpProcess.on('error', (err) => {
    console.error('Failed to start MCP Server:', err);
    mcpProcessReady = false;
  });
}

// MCP Protocol Handler
class MCPHandler {
  constructor() {
    this.requestId = 0;
    this.pendingRequests = new Map();
  }

  generateRequestId() {
    return ++this.requestId;
  }

  async sendRequest(method, params = {}) {
    if (!mcpProcessReady) {
      throw new Error('MCP Server is not ready');
    }

    const id = this.generateRequestId();
    const request = {
      jsonrpc: '2.0',
      id,
      method,
      params
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      
      // Send request to MCP server
      mcpProcess.stdin.write(JSON.stringify(request) + '\n');
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }

  handleResponse(response) {
    try {
      const data = JSON.parse(response);
      
      if (data.id && this.pendingRequests.has(data.id)) {
        const { resolve, reject } = this.pendingRequests.get(data.id);
        this.pendingRequests.delete(data.id);
        
        if (data.error) {
          reject(new Error(data.error.message || 'MCP Server error'));
        } else {
          resolve(data.result);
        }
      }
    } catch (error) {
      console.error('Error parsing MCP response:', error);
    }
  }
}

const mcpHandler = new MCPHandler();

// Create HTTP server
const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      mcpServerReady: mcpProcessReady,
      timestamp: new Date().toISOString()
    }));
    return;
  }

  if (req.url === '/mcp' && req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        const { method, params } = JSON.parse(body);
        
        if (!method) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Method is required' }));
          return;
        }

        const result = await mcpHandler.sendRequest(method, params);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ result }));
        
      } catch (error) {
        console.error('MCP HTTP Error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          error: error.message || 'Internal server error' 
        }));
      }
    });
    return;
  }

  // 404 for other routes
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Start the server
server.listen(PORT, () => {
  console.log(`🚀 Kavion MCP Remote Server running on port ${PORT}`);
  console.log(`📡 HTTP endpoint: http://localhost:${PORT}/mcp`);
  console.log(`❤️  Health check: http://localhost:${PORT}/health`);
  
  // Start MCP server
  startMCPServer();
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down gracefully...');
  
  if (mcpProcess) {
    mcpProcess.kill();
  }
  
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
  
  if (mcpProcess) {
    mcpProcess.kill();
  }
  
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});