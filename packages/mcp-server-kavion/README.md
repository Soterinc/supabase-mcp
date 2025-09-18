# Kavion Supabase MCP Server

> JWT-authenticated MCP server for secure user-level Supabase database access

![Kavion MCP Server](https://img.shields.io/badge/MCP-Server-blue) ![JWT](https://img.shields.io/badge/Auth-JWT-green) ![RLS](https://img.shields.io/badge/Security-RLS-red) ![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue)

A **user-focused MCP server** that provides secure, JWT-authenticated access to Supabase databases with Row Level Security (RLS) enforcement. Built on the official Supabase MCP framework but designed for **end-users** rather than project administrators.

## 🎯 Purpose

Unlike the official `@supabase/mcp-server-supabase` which is designed for **project management** using Personal Access Tokens (PAT), this server enables **user-level data access** using JWT authentication and RLS policies.

| Official Supabase MCP | Kavion Supabase MCP |
|-----------------------|---------------------|
| **Target**: Developers/Admins | **Target**: End Users |
| **Auth**: Personal Access Token | **Auth**: User Email/Password → JWT |
| **Access**: Project Management | **Access**: User Data with RLS |
| **Tools**: 20+ admin tools | **Tools**: 6 focused data tools |
| **Security**: Admin privileges | **Security**: Database-level RLS |

## 🚀 Features

### 🔐 **JWT Authentication Flow**
- Accepts user **email/password** credentials
- Automatically **generates JWT tokens**
- Enforces **Row Level Security (RLS)** policies
- Provides **user-specific data access**

### 🛠️ **Database Tools**
- **`execute_sql`** - Execute raw SQL queries with RLS enforcement
- **`list_tables`** - List database tables and schemas
- **`list_extensions`** - List PostgreSQL extensions
- **`apply_migration`** - Apply database migrations (with proper permissions)
- **`get_table_info`** - Get detailed table information
- **`search_docs`** - Search documentation and help

### 🔒 **Security Features**
- **Database-level security** via RLS policies
- **User-specific data filtering** based on organization membership
- **JWT token management** with automatic generation
- **Read-only mode** support for safe querying
- **Untrusted data boundaries** for SQL results

## 📦 Installation

### Prerequisites

- Node.js 18+ 
- pnpm (for monorepo management)
- Supabase project with RLS policies configured

### Build from Source

```bash
# Clone the repository
git clone https://github.com/your-username/mcp.git
cd mcp

# Install dependencies
pnpm install

# Build the server
cd packages/mcp-server-kavion
pnpm build

# Test the CLI
node dist/transports/stdio.js --help
```

## 🔧 Configuration

### CLI Arguments

```bash
# With user credentials (recommended)
mcp-server-kavion \
  --user-email user@example.com \
  --user-password mypassword \
  --read-only

# With pre-generated JWT token
mcp-server-kavion \
  --jwt-token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... \
  --read-only

# With custom features
mcp-server-kavion \
  --user-email user@example.com \
  --user-password mypassword \
  --features database,docs \
  --read-only
```

### Environment Variables

```bash
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
export USER_EMAIL=user@example.com
export USER_PASSWORD=mypassword
```

## 🎪 Cursor Integration

### Basic Configuration

```json
{
  "mcpServers": {
    "kavion-supabase": {
      "command": "node",
      "args": [
        "/path/to/mcp-server-kavion/dist/transports/stdio.js",
        "--read-only",
        "--user-email=user@example.com",
        "--user-password=mypassword"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_ANON_KEY": "your-anon-key"
      }
    }
  }
}
```

### Environment Variables (Secure)

```json
{
  "mcpServers": {
    "kavion-supabase": {
      "command": "node",
      "args": [
        "/path/to/mcp-server-kavion/dist/transports/stdio.js",
        "--read-only"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_ANON_KEY": "your-anon-key",
        "USER_EMAIL": "user@example.com",
        "USER_PASSWORD": "mypassword"
      }
    }
  }
}
```

### JWT Token Mode

```json
{
  "mcpServers": {
    "kavion-supabase": {
      "command": "node",
      "args": [
        "/path/to/mcp-server-kavion/dist/transports/stdio.js",
        "--jwt-token=your-jwt-token",
        "--read-only"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_ANON_KEY": "your-anon-key"
      }
    }
  }
}
```

### My Current Cursor Configuration

```json
"kavion-thermal-jwt": {
      "command": "node",
      "args": [
        "/home/behnam/git/KavApps/kavion-v0/temp/supabase-mcp/packages/mcp-server-kavion/dist/transports/stdio.js",
        "--read-only",
        "--features=database,docs",
        "--user-email=behnam.moradi@kavai.com",
        "--user-password=<password>"
      ],
      "env": {
        "SUPABASE_URL": "https://vwovgsttefakrjcaytin.supabase.co",
        "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3b3Znc3R0ZWZha3JqY2F5dGluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NTgxNDUsImV4cCI6MjA2MzMzNDE0NX0.3ZzaKTX6PS68f8-VPkwqr5ng4-Iwu5_aNlAffoM7zDQ"
      }
    }

```

## ⚙️ Setup Requirements

### 1. RPC Function (Required)

Create this function in your Supabase SQL Editor:

```sql
CREATE OR REPLACE FUNCTION execute_sql_query(sql_query text)
RETURNS json
LANGUAGE plpgsql
SECURITY INVOKER  -- Important: Uses caller's privileges for RLS
AS $$
DECLARE
  result json;
  rec record;
  results json[] := '{}';
BEGIN
  FOR rec IN EXECUTE sql_query LOOP
    results := results || row_to_json(rec);
  END LOOP;
  RETURN array_to_json(results);
EXCEPTION
  WHEN OTHERS THEN
    RAISE EXCEPTION 'SQL Error: %', SQLERRM;
END;
$$;
```

### 2. RLS Policies (Recommended)

Ensure your tables have proper RLS policies:

```sql
-- Enable RLS on your tables
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

-- Example policy for datasets
CREATE POLICY "Users can only see datasets from their organizations" 
ON datasets FOR SELECT 
TO authenticated 
USING (
  (owner_id = auth.uid()) OR 
  (organization_id IS NOT NULL AND is_org_member_secure(organization_id))
);
```

## 🎯 Usage Examples

### Query Your Data

```sql
-- List your accessible datasets
SELECT name, slug, description FROM datasets ORDER BY name;

-- Count images by type
SELECT 
  CASE 
    WHEN filename LIKE '%_T.%' THEN 'Thermal'
    WHEN filename LIKE '%_V.%' THEN 'RGB'
    ELSE 'Other'
  END as image_type,
  COUNT(*) as count
FROM images 
GROUP BY image_type;

-- Get GPS coverage
SELECT 
  d.name as dataset,
  COUNT(*) as total_images,
  COUNT(CASE WHEN i.metadata ? 'GPSLatitude' THEN 1 END) as gps_images
FROM datasets d
LEFT JOIN images i ON d.id = i.dataset_id
GROUP BY d.name
ORDER BY d.name;
```

### Explore Database Schema

```sql
-- List all your accessible tables
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;
```

## 🔒 Security

### Authentication Flow

1. **User provides email/password** → Server generates JWT token
2. **JWT token set** → Supabase client authenticated  
3. **RLS policies activated** → Database enforces user-specific access
4. **Queries filtered** → User only sees their organization's data

### Security Features

- ✅ **No admin privileges** - Users can't access other users' data
- ✅ **RLS enforcement** - Database-level security policies
- ✅ **JWT expiration** - Tokens have built-in expiration
- ✅ **Read-only mode** - Optional restriction to SELECT queries only
- ✅ **Untrusted data boundaries** - SQL results wrapped with security warnings

### Security Testing

Test with different users to verify RLS:

```bash
# Admin user - sees all accessible datasets
mcp-server-kavion --user-email admin@company.com --user-password pass

# Limited user - sees only their organization's datasets  
mcp-server-kavion --user-email user@company.com --user-password pass
```

## 🆚 Comparison with Official Server

| Feature | Official @supabase/mcp-server-supabase | Kavion mcp-server-kavion |
|---------|---------------------------------------|-------------------------|
| **Authentication** | Personal Access Token (PAT) | User Email/Password → JWT |
| **Target Users** | Supabase developers/admins | Application end-users |
| **Access Level** | Project management | User data with RLS |
| **Tool Count** | 20+ tools | 6 focused tools |
| **Security Model** | Admin privileges | User-level RLS |
| **Use Case** | Manage Supabase projects | Query user data securely |
| **Data Access** | Management API | Direct DB + RLS |
| **Setup Complexity** | Simple (just PAT) | Requires RLS setup |

## 🏗️ Architecture

### Built On
- **@supabase/mcp-utils** - Official MCP framework
- **@supabase/supabase-js** - Supabase client library
- **TypeScript** - Type-safe development
- **tsup** - Fast TypeScript bundler

### Platform Layer
- **JWT Platform** - Custom platform implementation
- **Database Operations** - RLS-aware SQL execution
- **Documentation** - Built-in help system

### Tool Structure
```
src/
├── server.ts              # Main server creation
├── platform/
│   ├── jwt-platform.ts    # JWT authentication platform
│   └── types.ts           # Platform type definitions
├── tools/
│   ├── database-operation-tools.ts  # SQL and schema tools
│   └── docs-tools.ts      # Documentation search
└── transports/
    └── stdio.ts           # CLI entry point
```

## 🐛 Troubleshooting

### Common Issues

**1. "Could not find function execute_sql_query"**
- Create the RPC function in your Supabase SQL Editor (see Setup Requirements)

**2. "Authentication failed"**
- Verify user email/password are correct
- Check SUPABASE_URL and SUPABASE_ANON_KEY

**3. "Can see all data (RLS not working)"**
- Verify RPC function uses `SECURITY INVOKER`
- Check RLS policies are properly configured
- Test with users who have limited organization access

**4. "No datasets visible"**
- Check user is member of organizations that own datasets
- Verify RLS policies allow organization member access

## 📄 License

Apache 2.0 - Same as official Supabase MCP server

## 🤝 Contributing

This server is based on the official Supabase MCP server architecture. Contributions welcome for:
- Additional user-level tools
- Better error handling
- Enhanced documentation
- Security improvements

## 🔗 Related Projects

- **[@supabase/mcp-server-supabase](https://github.com/supabase/mcp)** - Official project management server
- **[@supabase/mcp-server-postgrest](https://github.com/supabase/mcp)** - PostgREST API server
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP specification

---

**Built for users who need secure, JWT-authenticated access to their Supabase data without admin privileges.** 🔐✨