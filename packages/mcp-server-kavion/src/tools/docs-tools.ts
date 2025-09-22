import { z } from 'zod';
import type { Tool } from '@supabase/mcp-utils';
import { DATABASE_CONTEXT } from '../database-context.js';

export type DocsToolsOptions = {
  appUrl: string;
};

/**
 * Documentation and help tools
 */
export function getDocsTools({ appUrl }: DocsToolsOptions): Record<string, Tool> {
  return {
    search_docs: {
      description: 'Search Kavion thermal/RGB imagery documentation and help',
      parameters: z.object({
        query: z.string().describe('Search query for documentation'),
      }),
      execute: async ({ query }) => {
        // Enhanced documentation search including database context
        const docs = [
          {
            title: 'Database Schema and Context',
            content: 'Comprehensive database schema, relationships, and SQL query patterns for the Kavion thermal/RGB imagery analysis platform.',
            href: 'kavion://database-context',
            isResource: true,
          },
          {
            title: 'Thermal/RGB Image Analysis',
            content: 'Learn how to analyze thermal and RGB drone imagery pairs for industrial inspections.',
            href: `${appUrl}/docs/thermal-rgb-analysis`,
          },
          {
            title: 'Dataset Management',
            content: 'Organize and manage your thermal drone imagery datasets.',
            href: `${appUrl}/docs/dataset-management`,
          },
          {
            title: 'GPS and Geographic Analysis',
            content: 'Use GPS metadata for geographic clustering and flight mission analysis.',
            href: `${appUrl}/docs/gps-analysis`,
          },
          {
            title: 'Image Search and Filtering',
            content: 'Search and filter thermal and RGB images by various criteria.',
            href: `${appUrl}/docs/image-search`,
          },
        ];

        const queryLower = query.toLowerCase();
        const relevantDocs = docs.filter(doc => 
          doc.title.toLowerCase().includes(queryLower) ||
          doc.content.toLowerCase().includes(queryLower)
        );

        if (relevantDocs.length === 0) {
          return `No documentation found for "${query}". Available topics: thermal analysis, dataset management, GPS analysis, image search.`;
        }

        const response = [`Found ${relevantDocs.length} documentation result(s) for "${query}":`];
        
        relevantDocs.forEach((doc, i) => {
          if (doc.isResource) {
            response.push(`\n${i + 1}. **${doc.title}** (MCP Resource)`);
            response.push(`   ${doc.content}`);
            response.push(`   Access via: \`kavion://database-context\``);
          } else {
            response.push(`\n${i + 1}. **[${doc.title}](${doc.href})**`);
            response.push(`   ${doc.content}`);
          }
        });

        return response.join('\n');
      },
    },
  };
}