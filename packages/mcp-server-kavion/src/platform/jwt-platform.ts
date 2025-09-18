import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { 
  DatabaseOperations, 
  ExecuteSqlOptions, 
  Migration,
  ApplyMigrationOptions 
} from './types.js';

export type JwtPlatformOptions = {
  supabaseUrl: string;
  supabaseAnonKey: string;
  userEmail?: string;
  userPassword?: string;
  jwtToken?: string;
};

/**
 * JWT-based platform implementation that mimics the official Supabase platform
 * but uses JWT authentication instead of PAT (Personal Access Token)
 */
export async function createJwtPlatform(options: JwtPlatformOptions) {
  const { supabaseUrl, supabaseAnonKey, userEmail, userPassword, jwtToken } = options;
  
  // Create Supabase client
  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });

  // Generate or use JWT token
  let finalJwtToken = jwtToken;
  if (!finalJwtToken && userEmail && userPassword) {
    console.log(`🔐 Generating JWT token for user: ${userEmail}`);
    const { data, error } = await supabase.auth.signInWithPassword({
      email: userEmail,
      password: userPassword,
    });

    if (error) {
      throw new Error(`Authentication failed: ${error.message}`);
    }

    if (!data.session?.access_token) {
      throw new Error('No access token received from authentication');
    }

    finalJwtToken = data.session.access_token;
    console.log(`✅ JWT token generated successfully`);
  }

  if (!finalJwtToken) {
    throw new Error('JWT token required: Provide either jwtToken or userEmail+userPassword');
  }

  // Set JWT session for RLS
  await supabase.auth.setSession({
    access_token: finalJwtToken,
    refresh_token: finalJwtToken,
  });

  console.log(`🔒 JWT authentication established - RLS policies active`);

  // Database operations using JWT + RLS
  const database: DatabaseOperations = {
    async executeSql<T>(projectId: string, options: ExecuteSqlOptions): Promise<T[]> {
      const { query, read_only } = options;
      
      // For JWT mode, we need to create an RPC function or use alternative approach
      try {
        const { data, error } = await supabase.rpc('execute_sql_query', { 
          sql_query: query 
        });
        
        if (error) {
          if (error.code === '42883') { // function does not exist
            throw new Error(`SQL execution requires RPC function. Create this function in your database:

CREATE OR REPLACE FUNCTION execute_sql_query(sql_query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result json;
BEGIN
  EXECUTE sql_query INTO result;
  RETURN result;
EXCEPTION
  WHEN OTHERS THEN
    RAISE EXCEPTION 'SQL Error: %', SQLERRM;
END;
$$;`);
          }
          throw new Error(`SQL Error: ${error.message}`);
        }

        return data as T[];
      } catch (error) {
        throw new Error(`Failed to execute SQL: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    },

    async listMigrations(projectId: string): Promise<Migration[]> {
      try {
        // Try to get migrations from supabase_migrations table
        const { data, error } = await supabase
          .from('supabase_migrations')
          .select('version, name')
          .order('version');

        if (error) {
          throw new Error(`Failed to list migrations: ${error.message}`);
        }

        return (data || []).map(m => ({
          version: m.version,
          name: m.name || undefined,
        }));
      } catch (error) {
        // Return empty array if migrations table doesn't exist
        return [];
      }
    },

    async applyMigration(projectId: string, options: ApplyMigrationOptions): Promise<void> {
      const { name, query } = options;
      
      try {
        // Execute the migration query
        const { error } = await supabase.rpc('execute_sql_query', { 
          sql_query: query 
        });
        
        if (error) {
          throw new Error(`Migration failed: ${error.message}`);
        }

        // Record the migration
        const { error: recordError } = await supabase
          .from('supabase_migrations')
          .insert({
            version: new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14),
            name,
            statements: [query],
          });

        if (recordError) {
          console.warn(`⚠️ Migration executed but not recorded: ${recordError.message}`);
        }
      } catch (error) {
        throw new Error(`Failed to apply migration: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    },
  };

  return {
    database,
    // Note: Other operations (account, functions, etc.) would require Management API access
    // For JWT mode, we focus on database operations since that's what users typically need
  };
}