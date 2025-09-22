#!/usr/bin/env node

const http = require('http');

const SERVER_URL = 'http://localhost:3000';

// Test HTTP endpoint
async function testHTTP() {
  console.log('🧪 Testing HTTP endpoint...');
  
  try {
    // Test health check
    const healthResponse = await new Promise((resolve, reject) => {
      const req = http.get(`${SERVER_URL}/health`, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      });
      req.on('error', reject);
    });
    
    console.log('✅ Health check:', healthResponse);
    
    // Test MCP tools list
    const toolsResponse = await new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        method: 'tools/list'
      });
      
      const options = {
        hostname: 'localhost',
        port: 3000,
        path: '/mcp',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        }
      };
      
      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      });
      
      req.on('error', reject);
      req.write(postData);
      req.end();
    });
    
    console.log('✅ Tools list:', toolsResponse);
    
    // Test SQL execution
    const sqlResponse = await new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        method: 'tools/call',
        params: {
          name: 'execute_sql',
          arguments: { query: 'SELECT COUNT(*) FROM datasets;' }
        }
      });
      
      const options = {
        hostname: 'localhost',
        port: 3000,
        path: '/mcp',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        }
      };
      
      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      });
      
      req.on('error', reject);
      req.write(postData);
      req.end();
    });
    
    console.log('✅ SQL execution:', sqlResponse);
    
  } catch (error) {
    console.error('❌ HTTP test failed:', error.message);
  }
}

// Run tests
async function runTests() {
  console.log('🚀 Starting Kavion MCP Remote Server Tests\n');
  
  await testHTTP();
  
  console.log('\n✅ All tests completed!');
  process.exit(0);
}

runTests().catch(console.error);