import { createMcpServer, type Tool, resources, jsonResource, jsonResourceResponse } from '@supabase/mcp-utils';
import packageJson from '../package.json' with { type: 'json' };
import { createJwtPlatform } from './platform/jwt-platform.js';
import { getDatabaseTools } from './tools/database-operation-tools.js';
import { getDocsTools } from './tools/docs-tools.js';
import { getKavionDomainTools } from './tools/kavion-domain-tools.js';
import { DATABASE_CONTEXT } from './database-context.js';

const { version } = packageJson;

export type KavionMcpServerOptions = {
  /**
   * Supabase project URL
   */
  supabaseUrl: string;
  
  /**
   * Supabase anon key (for authentication)
   */
  supabaseAnonKey: string;
  
  /**
   * User email for authentication
   */
  userEmail?: string;
  
  /**
   * User password for authentication
   */
  userPassword?: string;
  
  /**
   * Pre-generated JWT token (alternative to email/password)
   */
  jwtToken?: string;
  
  /**
   * The project ID to scope the server to (for compatibility with official server)
   */
  projectId?: string;
  
  /**
   * Executes database queries in read-only mode if true
   */
  readOnly?: boolean;
  
  /**
   * Features to enable
   * Options: 'database', 'docs'
   */
  features?: string[];
  
  /**
   * Frontend app URL for generating clickable links
   */
  appUrl?: string;
  
  /**
   * Custom database context content (overrides default)
   */
  databaseContext?: string;
};

const DEFAULT_FEATURES = ['docs', 'database'];

/**
 * Creates a Supabase MCP server that uses JWT authentication instead of PAT
 * Structure mirrors the official server but with user-level authentication
 */
export function createKavionMcpServer(options: KavionMcpServerOptions): ReturnType<typeof createMcpServer> {
  const {
    supabaseUrl,
    supabaseAnonKey,
    userEmail,
    userPassword,
    jwtToken,
    projectId,
    readOnly = false,
    features = DEFAULT_FEATURES,
    appUrl = 'http://localhost:3000',
    databaseContext,
  } = options;

  const server = createMcpServer({
    name: 'kavion-supabase-jwt',
    version,
    resources: resources('kavion', [
      jsonResource('/database-context', {
        name: 'Database Context',
        description: 'Comprehensive database schema and context for LLM SQL generation',
        async read(uri) {
          // Use custom database context if provided, otherwise fall back to default
          let contextContent = databaseContext || process.env.DATABASE_CONTEXT;
          
          // If no custom context provided, try to load from local database_context.md
          if (!contextContent) {
            try {
              const fs = await import('fs');
              const path = await import('path');
              const localContextFile = path.join(process.cwd(), 'database_context.md');
              if (fs.existsSync(localContextFile)) {
                contextContent = fs.readFileSync(localContextFile, 'utf-8');
                console.log(`✅ Auto-loaded database context from: ${localContextFile}`);
              }
            } catch (error) {
              console.log(`⚠️ Could not load local database_context.md: ${error}`);
            }
          }
          
          // Fall back to default if no custom context found
          if (!contextContent) {
            contextContent = DATABASE_CONTEXT;
          }
          
          return jsonResourceResponse(uri, {
            content: contextContent,
            mimeType: 'text/markdown',
            lastModified: new Date().toISOString(),
          });
        },
      }),
    ]),
    async onInitialize(info) {
      console.log(`🔥❄️ Kavion Supabase MCP Server v${version} initialized`);
      console.log(`🔗 App URL: ${appUrl}`);
      console.log(`🔒 Read-only mode: ${readOnly}`);
      console.log(`🛠️ Features: ${features.join(', ')}`);
      if (userEmail) console.log(`👤 User: ${userEmail}`);
      if (jwtToken) console.log(`🔐 Pre-generated JWT token provided`);
      if (userEmail && userPassword) console.log(`🔐 Will generate JWT from user credentials`);
    },
    tools: async () => {
      const tools: Record<string, Tool> = {};

      // Create JWT platform (similar to official API platform)
      const platform = await createJwtPlatform({
        supabaseUrl,
        supabaseAnonKey,
        userEmail,
        userPassword,
        jwtToken,
      });

      // Add docs tools if enabled (similar to official server)
      if (features.includes('docs')) {
        Object.assign(tools, getDocsTools({ appUrl }));
      }

      // Add database tools if enabled (similar to official server)
      if (features.includes('database') && platform.database) {
        Object.assign(tools, getDatabaseTools({
          database: platform.database,
          projectId,
          readOnly,
        }));
      }

      // Add Kavion domain tools (always enabled)
      if (platform.database) {
        // Generate JWT token if not provided
        let finalJwtToken = jwtToken;
        if (!finalJwtToken && userEmail && userPassword) {
          const { createClient } = await import('@supabase/supabase-js');
          const supabase = createClient(supabaseUrl, supabaseAnonKey);
          const { data } = await supabase.auth.signInWithPassword({
            email: userEmail,
            password: userPassword,
          });
          finalJwtToken = data.session?.access_token;
        }
        
        if (finalJwtToken) {
          Object.assign(tools, getKavionDomainTools({
            supabaseUrl,
            supabaseAnonKey,
            appUrl,
            jwtToken: finalJwtToken,
          }));
        }
      }

      console.log(`🚀 Total tools available: ${Object.keys(tools).length}`);
      return tools;
    },
  });

  return server;
}