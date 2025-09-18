import { createMcpServer, type Tool } from '@supabase/mcp-utils';
import { createClient } from '@supabase/supabase-js';
import packageJson from '../package.json' with { type: 'json' };
import { getKavionDomainTools } from './tools/kavion-domain-tools.js';
import { getOfficialDatabaseTools } from './tools/official-database-tools.js';

const { version } = packageJson;

/**
 * Generate JWT token from user email and password
 */
async function generateJwtToken(supabaseUrl: string, supabaseAnonKey: string, email: string, password: string): Promise<string> {
  const supabase = createClient(supabaseUrl, supabaseAnonKey);
  
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    throw new Error(`Authentication failed: ${error.message}`);
  }

  if (!data.session?.access_token) {
    throw new Error('No access token received from authentication');
  }

  return data.session.access_token;
}

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
   * Frontend app URL for generating clickable links
   */
  appUrl?: string;
  
  /**
   * Read-only mode for SQL operations
   */
  readOnly?: boolean;
  
  /**
   * Enable official SQL tools alongside domain tools
   */
  enableSqlTools?: boolean;
};

/**
 * Creates a hybrid MCP server that combines:
 * 1. Domain-specific thermal/RGB imagery tools (rich UX)
 * 2. Official SQL database tools (query flexibility)
 */
export function createKavionMcpServer(options: KavionMcpServerOptions): ReturnType<typeof createMcpServer> {
  const {
    supabaseUrl,
    supabaseAnonKey,
    userEmail,
    userPassword,
    jwtToken,
    appUrl = 'http://localhost:3000',
    readOnly = false,
    enableSqlTools = true,
  } = options;

  const server = createMcpServer({
    name: 'kavion-thermal-imagery',
    version,
    async onInitialize(info) {
      console.log(`🔥❄️ Kavion Thermal/RGB MCP Server v${version} initialized`);
      console.log(`🔗 App URL: ${appUrl}`);
      console.log(`🔒 Read-only mode: ${readOnly}`);
      console.log(`🛠️ SQL tools enabled: ${enableSqlTools}`);
      if (userEmail) console.log(`👤 User: ${userEmail}`);
      if (jwtToken) console.log(`🔐 Pre-generated JWT token provided`);
      if (userEmail && userPassword) console.log(`🔐 Will generate JWT from user credentials`);
    },
    tools: async () => {
      const tools: Record<string, Tool> = {};

      // Generate JWT token if user credentials provided
      let finalJwtToken = jwtToken;
      if (!finalJwtToken && userEmail && userPassword) {
        console.log(`🔐 Generating JWT token for user: ${userEmail}`);
        try {
          finalJwtToken = await generateJwtToken(supabaseUrl, supabaseAnonKey, userEmail, userPassword);
          console.log(`✅ JWT token generated successfully`);
        } catch (error) {
          console.error(`❌ Failed to generate JWT token:`, error);
          throw new Error(`Authentication failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }

      if (!finalJwtToken) {
        throw new Error('Authentication required: Provide either jwtToken or userEmail+userPassword');
      }

      // Add domain-specific tools (your custom thermal/RGB tools)
      const domainTools = getKavionDomainTools({ 
        supabaseUrl, 
        supabaseAnonKey, 
        appUrl,
        jwtToken: finalJwtToken,
      });
      Object.assign(tools, domainTools);
      console.log(`✅ Loaded ${Object.keys(domainTools).length} domain-specific tools`);

      // Optionally add official SQL tools
      if (enableSqlTools) {
        const sqlTools = getOfficialDatabaseTools({ 
          supabaseUrl, 
          supabaseAnonKey, 
          readOnly,
          jwtToken: finalJwtToken,
        });
        Object.assign(tools, sqlTools);
        console.log(`✅ Loaded ${Object.keys(sqlTools).length} SQL database tools`);
      }

      console.log(`🚀 Total tools available: ${Object.keys(tools).length}`);
      return tools;
    },
  });

  return server;
}