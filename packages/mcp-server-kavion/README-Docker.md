# Kavion MCP Server - Docker Deployment

This document explains how to deploy the Kavion MCP Server as an HTTP server using Docker.

## 🐳 Docker Setup

### Prerequisites

- Docker and Docker Compose installed
- Access to Supabase database
- Valid user credentials

### Quick Start

1. **Clone and navigate to the directory:**
   ```bash
   cd /home/behnam/git/KavApps/kavion-v0/mcp/supabase-mcp/packages/mcp-server-kavion
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Or build and run manually:**
   ```bash
   # Build the image
   docker build -t kavion-mcp-server .
   
   # Run the container
   docker run -p 3000:3000 \
     -e SUPABASE_URL=https://vwovgsttefakrjcaytin.supabase.co \
     -e SUPABASE_ANON_KEY=your_supabase_key \
     -e USER_EMAIL=your_email@example.com \
     -e USER_PASSWORD=your_password \
     kavion-mcp-server
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Required |
| `USER_EMAIL` | User email for authentication | Required |
| `USER_PASSWORD` | User password for authentication | Required |
| `PORT` | HTTP server port | 3000 |
| `NODE_ENV` | Node.js environment | production |

### Docker Compose

The `docker-compose.yml` file includes:
- Health checks
- Automatic restart policy
- Network configuration
- Environment variable support

## 🌐 HTTP Endpoints

Once running, the server provides:

- **Health Check:** `GET http://localhost:3000/health`
- **MCP Endpoint:** `POST http://localhost:3000/mcp`

### MCP Endpoint Usage

```bash
# List available tools
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'

# Execute SQL query
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {
        "query": "SELECT COUNT(*) FROM datasets"
      }
    }
  }'
```

## 🚀 Production Deployment

### Using Docker Compose (Recommended)

1. **Set environment variables:**
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_ANON_KEY="your_supabase_key"
   export USER_EMAIL="your_email"
   export USER_PASSWORD="your_password"
   ```

2. **Deploy:**
   ```bash
   docker-compose up -d
   ```

3. **Check status:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml kavion-mcp
```

### Using Kubernetes

Create a Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kavion-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kavion-mcp-server
  template:
    metadata:
      labels:
        app: kavion-mcp-server
    spec:
      containers:
      - name: kavion-mcp-server
        image: kavion-mcp-server:latest
        ports:
        - containerPort: 3000
        env:
        - name: SUPABASE_URL
          value: "your_supabase_url"
        - name: SUPABASE_ANON_KEY
          value: "your_supabase_key"
        - name: USER_EMAIL
          value: "your_email"
        - name: USER_PASSWORD
          value: "your_password"
---
apiVersion: v1
kind: Service
metadata:
  name: kavion-mcp-service
spec:
  selector:
    app: kavion-mcp-server
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

## 🔍 Monitoring

### Health Checks

The container includes health checks:
- **Endpoint:** `GET /health`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds
- **Retries:** 3

### Logs

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f kavion-mcp-server
```

### Metrics

Monitor the server using:
- Docker stats: `docker stats`
- Health endpoint: `curl http://localhost:3000/health`
- Application logs

## 🛠️ Development

### Local Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run the HTTP server locally
node dist/transports/http.js \
  --apiUrl https://vwovgsttefakrjcaytin.supabase.co \
  --apiKey your_key \
  --userEmail your_email \
  --userPassword your_password
```

### Debugging

```bash
# Run with debug logs
docker run -p 3000:3000 \
  -e NODE_ENV=development \
  -e DEBUG=* \
  kavion-mcp-server
```

## 🔒 Security

### Best Practices

1. **Use environment variables** for sensitive data
2. **Run as non-root user** (already configured)
3. **Use HTTPS** in production
4. **Implement rate limiting**
5. **Monitor access logs**

### Network Security

```bash
# Create custom network
docker network create kavion-network

# Run with custom network
docker run --network kavion-network kavion-mcp-server
```

## 📚 API Documentation

### Available Tools

1. **execute_sql** - Execute SQL queries
2. **list_tables** - List database tables
3. **search_docs** - Search documentation

### Error Handling

The server returns appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

## 🆘 Troubleshooting

### Common Issues

1. **Container won't start:**
   ```bash
   docker-compose logs kavion-mcp-server
   ```

2. **Database connection issues:**
   - Check Supabase URL and key
   - Verify user credentials
   - Check network connectivity

3. **Port conflicts:**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "3001:3000"
   ```

### Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Test the health endpoint
4. Check Supabase connectivity
