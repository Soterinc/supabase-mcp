#!/usr/bin/env node

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { parseArgs } from 'node:util';
import packageJson from '../../package.json' with { type: 'json' };
import { createKavionMcpServer } from '../server.js';

const { version } = packageJson;

async function main() {
  const {
    values: {
      ['supabase-url']: supabaseUrl,
      ['supabase-anon-key']: supabaseAnonKey,
      ['user-email']: userEmail,
      ['user-password']: userPassword,
      ['jwt-token']: jwtToken,
      ['project-ref']: projectId,
      ['app-url']: appUrl,
      ['read-only']: readOnly,
      ['features']: featuresArg,
      ['version']: showVersion,
      ['help']: showHelp,
    },
  } = parseArgs({
    options: {
      ['supabase-url']: { 
        type: 'string',
      },
      ['supabase-anon-key']: { 
        type: 'string',
      },
      ['user-email']: { 
        type: 'string',
      },
      ['user-password']: { 
        type: 'string',
      },
      ['jwt-token']: { 
        type: 'string',
      },
      ['project-ref']: { 
        type: 'string',
      },
      ['app-url']: { 
        type: 'string',
      },
      ['read-only']: { 
        type: 'boolean', 
        default: false,
      },
      ['features']: { 
        type: 'string',
      },
      ['version']: { 
        type: 'boolean',
      },
      ['help']: { 
        type: 'boolean',
      },
    },
  });

  if (showVersion) {
    console.log(version);
    process.exit(0);
  }

  if (showHelp) {
    console.log(`
🔥❄️ Kavion Thermal/RGB MCP Server v${version}

Usage: mcp-server-kavion [options]

Options:
      --supabase-url <url>     Supabase project URL
      --supabase-anon-key <key> Supabase anonymous key
      --user-email <email>     User email for authentication
      --user-password <pass>   User password for authentication
      --jwt-token <token>      Pre-generated JWT token (alternative to email/password)
      --project-ref <ref>      Project reference ID (optional)
      --app-url <url>          Frontend app URL (default: http://localhost:3000)
      --read-only              Enable read-only mode for SQL operations
      --features <features>    Comma-separated features to enable (database,docs)
      --version                Show version number
      --help                   Show this help message

Environment Variables:
  SUPABASE_URL                 Supabase project URL
  SUPABASE_ANON_KEY            Supabase anonymous key
  USER_EMAIL                   User email for authentication
  USER_PASSWORD                User password for authentication
  NEXT_PUBLIC_APP_URL          Frontend app URL

Examples:
  # With user credentials (generates JWT automatically)
  mcp-server-kavion --user-email user@example.com --user-password mypassword

  # With pre-generated JWT token
  mcp-server-kavion --jwt-token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

  # Using environment variables
  export SUPABASE_URL=https://xxx.supabase.co
  export SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  export USER_EMAIL=user@example.com
  export USER_PASSWORD=mypassword
  mcp-server-kavion

  # Read-only mode without SQL tools
  mcp-server-kavion --user-email user@example.com --user-password mypassword --read-only --enable-sql=false
`);
    process.exit(0);
  }

  const finalSupabaseUrl = supabaseUrl ?? process.env.SUPABASE_URL;
  const finalSupabaseAnonKey = supabaseAnonKey ?? process.env.SUPABASE_ANON_KEY;
  const finalUserEmail = userEmail ?? process.env.USER_EMAIL;
  const finalUserPassword = userPassword ?? process.env.USER_PASSWORD;
  const finalJwtToken = jwtToken;
  const finalProjectId = projectId;
  const finalAppUrl = appUrl ?? process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000';
  const finalFeatures = featuresArg ? featuresArg.split(',') : ['database', 'docs'];

  if (!finalSupabaseUrl || !finalSupabaseAnonKey) {
    console.error(`❌ Error: Missing required Supabase configuration

Please provide:
1. Supabase URL: --supabase-url or SUPABASE_URL env var
2. Supabase Anon Key: --supabase-anon-key or SUPABASE_ANON_KEY env var

Run 'mcp-server-kavion --help' for more information.`);
    process.exit(1);
  }

  if (!finalJwtToken && (!finalUserEmail || !finalUserPassword)) {
    console.error(`❌ Error: Authentication required

Please provide either:
1. JWT Token: --jwt-token <token>
2. User Credentials: --user-email <email> --user-password <password>

Or set environment variables: USER_EMAIL and USER_PASSWORD

Run 'mcp-server-kavion --help' for more information.`);
    process.exit(1);
  }

  console.log(`🚀 Starting Kavion Thermal/RGB MCP Server v${version}`);
  
  try {
    const server = createKavionMcpServer({
      supabaseUrl: finalSupabaseUrl,
      supabaseAnonKey: finalSupabaseAnonKey,
      userEmail: finalUserEmail,
      userPassword: finalUserPassword,
      jwtToken: finalJwtToken,
      projectId: finalProjectId,
      appUrl: finalAppUrl,
      readOnly,
      features: finalFeatures,
    });

    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.log(`✅ Server connected and ready!`);
  } catch (error) {
    console.error(`❌ Failed to start server:`, error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error('❌ Unexpected error:', error);
  process.exit(1);
});