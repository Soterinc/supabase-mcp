# Kavion Custom MCP Server

A hybrid MCP server that combines domain-specific thermal/RGB drone imagery tools with flexible SQL database access.

## Features

### 🔥❄️ Domain-Specific Tools
- **`list_datasets`** - Lists thermal/RGB datasets with clickable links
- **`smart_image_search`** - Search and display images with thumbnails  
- **`ask_about_dataset`** - Detailed dataset analysis and statistics
- **`get_quick_stats`** - Quick database overview

### 🗃️ SQL Database Tools (Optional)
- **`execute_sql`** - Execute raw SQL queries
- **`list_tables`** - List database tables and schemas
- **`list_extensions`** - List PostgreSQL extensions
- **`get_table_info`** - Detailed table information

## Installation & Usage

### Build from Source

```bash
# Install dependencies
pnpm install

# Build the server
pnpm build

# Test the CLI
node dist/transports/stdio.js --help
```

### Configuration Options

```bash
# Basic usage with environment variables
mcp-server-kavion

# With explicit configuration  
mcp-server-kavion --supabase-url https://xxx.supabase.co --supabase-key your-key

# Read-only mode without SQL tools
mcp-server-kavion --read-only --enable-sql=false

# With JWT authentication (RLS enabled)
mcp-server-kavion --jwt-token your-jwt-token --user-id user-uuid
```

## Cursor Integration

### Option 1: Read-Only Domain Tools Only
```json
{
  "mcpServers": {
    "kavion-thermal": {
      "command": "node",
      "args": [
        "/path/to/dist/transports/stdio.js",
        "--read-only",
        "--enable-sql=false"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      }
    }
  }
}
```

### Option 2: Hybrid Domain + SQL Tools
```json
{
  "mcpServers": {
    "kavion-thermal-full": {
      "command": "node",
      "args": [
        "/path/to/dist/transports/stdio.js",
        "--enable-sql=true"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co", 
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      }
    }
  }
}
```

### Option 3: JWT Authentication with RLS
```json
{
  "mcpServers": {
    "kavion-thermal-jwt": {
      "command": "node",
      "args": [
        "/path/to/dist/transports/stdio.js",
        "--jwt-token=your-jwt-token"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_ANON_KEY": "your-anon-key"
      }
    }
  }
}
```

## Environment Variables

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key (admin access)
- `SUPABASE_ANON_KEY` - Anonymous key (for JWT mode)
- `NEXT_PUBLIC_APP_URL` - Frontend app URL for clickable links

## Architecture

This server combines two approaches:

### Domain-Specific Tools (Rich UX)
- Provides formatted responses with thumbnails and links
- Understands thermal/RGB imagery concepts
- Returns structured markdown for better presentation
- Optimized for common thermal imagery workflows

### SQL Tools (Query Flexibility)  
- Allows complex database queries via raw SQL
- Respects RLS policies when using JWT authentication
- Provides escape hatch for advanced analysis
- Returns JSON data with security boundaries

## Comparison with Official Supabase MCP

| Feature | Official Server | Kavion Custom Server |
|---------|----------------|---------------------|
| **Approach** | Query-first SQL access | Domain-first with SQL option |
| **User Experience** | Technical, requires SQL | User-friendly, domain-aware |
| **Output Format** | Raw JSON with warnings | Rich markdown with images |
| **Domain Knowledge** | Generic database | Thermal/RGB imagery expertise |
| **Authentication** | Service role + RLS | Service role, JWT, or dual auth |

## Development

Based on the official Supabase MCP server architecture but customized for thermal/RGB drone imagery workflows.

### Key Dependencies
- `@supabase/mcp-utils` - MCP framework utilities
- `@supabase/supabase-js` - Supabase client
- `zod` - Schema validation

### Build System
- TypeScript compilation with `tsup`
- ESM and CJS output formats
- CLI entry point with argument parsing