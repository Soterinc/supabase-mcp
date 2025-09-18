import { z } from 'zod';

export const executeSqlOptionsSchema = z.object({
  query: z.string(),
  read_only: z.boolean().optional(),
});

export const applyMigrationOptionsSchema = z.object({
  name: z.string(),
  query: z.string(),
});

export const migrationSchema = z.object({
  version: z.string(),
  name: z.string().optional(),
});

export type ExecuteSqlOptions = z.infer<typeof executeSqlOptionsSchema>;
export type ApplyMigrationOptions = z.infer<typeof applyMigrationOptionsSchema>;
export type Migration = z.infer<typeof migrationSchema>;

export type DatabaseOperations = {
  executeSql<T>(projectId: string, options: ExecuteSqlOptions): Promise<T[]>;
  listMigrations(projectId: string): Promise<Migration[]>;
  applyMigration(projectId: string, options: ApplyMigrationOptions): Promise<void>;
};

export type SupabasePlatform = {
  database?: DatabaseOperations;
};