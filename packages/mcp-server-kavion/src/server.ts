import { createMcpServer, type Tool } from '@supabase/mcp-utils';
import packageJson from '../package.json' with { type: 'json' };
import { createJwtPlatform } from './platform/jwt-platform.js';
import { getDatabaseTools } from './tools/database-operation-tools.js';
import { getDocsTools } from './tools/docs-tools.js';
import { getKavionDomainTools } from './tools/kavion-domain-tools.js';

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
  } = options;

  const server = createMcpServer({
    name: 'kavion-supabase-jwt',
    version,
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