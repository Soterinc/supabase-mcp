import { z } from 'zod';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { Tool } from '@supabase/mcp-utils';

export type KavionDomainToolsOptions = {
  supabaseUrl: string;
  supabaseAnonKey: string;
  appUrl: string;
  jwtToken: string;
};

/**
 * Creates domain-specific tools for thermal/RGB drone imagery analysis
 * These tools provide rich, formatted responses with thumbnails and clickable links
 */
export function getKavionDomainTools(options: KavionDomainToolsOptions): Record<string, Tool> {
  const { supabaseUrl, supabaseAnonKey, appUrl, jwtToken } = options;
  
  // Create Supabase client with anon key
  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });

  // Set JWT token for RLS authentication
  supabase.auth.setSession({
    access_token: jwtToken,
    refresh_token: jwtToken,
  });

  return {
    // DISABLED TOOLS - Commented out as requested
    // list_datasets: {
    //   description: 'Lists all available thermal/RGB drone imagery datasets with clickable links and image counts. This is typically the FIRST step - use the dataset slugs returned here for other tools.',
    //   parameters: z.object({}),
    //   execute: async () => {
    //     try {
    //       const { data: datasets, error } = await supabase
    //         .from('datasets')
    //         .select('id, name, slug, description')
    //         .order('name');

    //       if (error) {
    //         return 'Error fetching datasets: ' + error.message;
    //       }

    //       if (!datasets?.length) {
    //         return 'No datasets found in your database.';
    //       }

    //       const response = ['Available Datasets:', ''];
          
    //       for (let i = 0; i < datasets.length; i++) {
    //         const dataset = datasets[i];
            
    //         // Get image count for each dataset
    //         const { count: imageCount, error: countError } = await supabase
    //           .from('images')
    //           .select('*', { count: 'exact', head: true })
    //           .eq('dataset_id', dataset.id);

    //         const count = countError ? 0 : (imageCount || 0);
    //         const datasetUrl = `${appUrl}/datasets/${dataset.slug}`;
            
    //         response.push(
    //           `${i + 1}. [${dataset.name}](${datasetUrl}) (${dataset.slug}) - ${count.toLocaleString()} images`
    //         );
            
    //         if (dataset.description?.trim()) {
    //           response.push(`   Description: ${dataset.description}`);
    //         }
    //       }
          
    //       response.push('');
    //       response.push(`Total: ${datasets.length} datasets with thermal/RGB drone imagery`);
    //       response.push('Ask me about specific datasets using their slug (e.g., "wacker-2024")');
          
    //       return response.join('\n');
    //     } catch (error) {
    //       return 'Error listing datasets: ' + (error instanceof Error ? error.message : 'Unknown error');
    //     }
    //   },
    // },

    // smart_image_search: {
    //   description: 'Search and display thermal/RGB images with actual thumbnails from a specific dataset. ALWAYS use this when users ask to see, show, display, or find images.',
    //   parameters: z.object({
    //     dataset_slug: z.string().describe('Dataset slug (get from list_datasets tool first)'),
    //     query: z.string().describe('Search query - use "thermal" for thermal images, "rgb" or "visual" for RGB images'),
    //     limit: z.number().min(1).max(50).default(10).describe('Number of images to return (1-50)'),
    //   }),
    //   execute: async ({ dataset_slug, query, limit }) => {
    //     try {
    //       // Find dataset first
    //       const { data: dataset, error: datasetError } = await supabase
    //         .from('datasets')
    //         .select('id, name')
    //         .eq('slug', dataset_slug)
    //         .single();

    //       if (datasetError || !dataset) {
    //         return `Dataset '${dataset_slug}' not found. Use list_datasets tool first to get available datasets.`;
    //       }

    //       // Build image query with filters
    //       let imageQuery = supabase
    //         .from('images')
    //         .select('id, filename, thumbnail_url, metadata, created_at')
    //         .eq('dataset_id', dataset.id)
    //         .order('created_at', { ascending: false })
    //         .limit(limit);

    //       // Apply filters based on query
    //       const queryLower = query.toLowerCase();
    //       if (queryLower.includes('thermal')) {
    //         imageQuery = imageQuery.ilike('filename', '%_T.%');
    //       } else if (queryLower.includes('rgb') || queryLower.includes('visual')) {
    //         imageQuery = imageQuery.ilike('filename', '%_V.%');
    //       } else if (queryLower.includes('dji')) {
    //         imageQuery = imageQuery.ilike('filename', '%DJI%');
    //       }

    //       const { data: images, error: imagesError } = await imageQuery;

    //       if (imagesError) {
    //         return 'Error searching images: ' + imagesError.message;
    //       }

    //       if (!images?.length) {
    //         return `No images found matching '${query}' in ${dataset.name} dataset`;
    //       }

    //       const response = [
    //         `Found ${images.length} images from the ${dataset.name} dataset:`,
    //         '',
    //       ];

    //       images.forEach((img, i) => {
    //         const filename = img.filename.split('/').pop() || img.filename;
    //         const typeIndicator = filename.includes('_T.') ? 'THERMAL' : 
    //                              filename.includes('_V.') ? 'RGB' : 'IMAGE';
            
    //         response.push(`${i + 1}. ${typeIndicator} ${filename} (ID: ${img.id})`);
            
    //         if (img.thumbnail_url) {
    //           response.push(`![${filename}](${img.thumbnail_url})`);
    //         } else {
    //           response.push('(No thumbnail available)');
    //         }
            
    //         // Add GPS info if available
    //         if (img.metadata?.GPSLatitude && img.metadata?.GPSLongitude) {
    //           response.push(`GPS: ${img.metadata.GPSLatitude}, ${img.metadata.GPSLongitude}`);
    //         }
            
    //         response.push('');
    //       });

    //       if (images.length === limit) {
    //         response.push(`Showing first ${limit} results. Ask for more images if needed.`);
    //       }

    //       return response.join('\n');
    //     } catch (error) {
    //       return 'Error searching images: ' + (error instanceof Error ? error.message : 'Unknown error');
    //     }
    //   },
    // },

    // ask_about_dataset: {
    //   description: 'Get detailed information and analysis about a specific dataset. Use this for questions like "tell me about dataset X" or "analyze dataset Y".',
    //   parameters: z.object({
    //     dataset_slug: z.string().describe('Dataset slug (get from list_datasets tool first)'),
    //     question: z.string().describe('Natural language question about the dataset'),
    //   }),
    //   execute: async ({ dataset_slug, question }) => {
    //     try {
    //       // Find dataset
    //       const { data: dataset, error: datasetError } = await supabase
    //         .from('datasets')
    //         .select('*')
    //         .eq('slug', dataset_slug)
    //         .single();

    //       if (datasetError || !dataset) {
    //         return `Dataset '${dataset_slug}' not found. Use list_datasets tool first.`;
    //       }

    //       // Get images for analysis
    //       const { data: images, error: imagesError } = await supabase
    //         .from('images')
    //         .select('id, filename, metadata, created_at')
    //         .eq('dataset_id', dataset.id);

    //       if (imagesError) {
    //         return 'Error fetching images: ' + imagesError.message;
    //       }

    //       const totalImages = images?.length || 0;
    //       const thermalImages = images?.filter(img => img.filename.includes('_T.')) || [];
    //       const rgbImages = images?.filter(img => img.filename.includes('_V.')) || [];
    //       const gpsImages = images?.filter(img => 
    //         img.metadata?.GPSLatitude && img.metadata?.GPSLongitude
    //       ) || [];

    //       const response = [
    //         `Dataset Analysis: ${dataset.name}`,
    //         '',
    //         'Overview:',
    //         `Total images: ${totalImages.toLocaleString()}`,
    //         `Thermal images: ${thermalImages.length.toLocaleString()}`,
    //         `RGB images: ${rgbImages.length.toLocaleString()}`,
    //         `Images with GPS: ${gpsImages.length.toLocaleString()} (${totalImages > 0 ? Math.round(gpsImages.length / totalImages * 100) : 0}%)`,
    //         '',
    //       ];

    //       // Pairing analysis
    //       if (thermalImages.length > 0 && rgbImages.length > 0) {
    //         const thermalBases = new Set(thermalImages.map(img => 
    //           img.filename.replace('_T.', '.').split('/').pop()?.split('.')[0]
    //         ));
    //         const rgbBases = new Set(rgbImages.map(img => 
    //           img.filename.replace('_V.', '.').split('/').pop()?.split('.')[0]
    //         ));
            
    //         const pairs = [...thermalBases].filter(base => rgbBases.has(base)).length;
    //         const pairingEfficiency = Math.round(pairs / Math.min(thermalImages.length, rgbImages.length) * 100);
            
    //         response.push('Thermal/RGB Pairing:');
    //         response.push(`Successfully paired: ${pairs.toLocaleString()}`);
    //         response.push(`Pairing efficiency: ${pairingEfficiency}%`);
            
    //         if (pairingEfficiency === 100) {
    //           response.push('Perfect pairing - every thermal has an RGB match!');
    //         } else if (pairingEfficiency > 90) {
    //           response.push('Excellent pairing with minimal missing matches');
    //         } else {
    //           response.push('Some images are missing their thermal/RGB counterparts');
    //         }
    //         response.push('');
    //       }

    //       // GPS analysis
    //       if (gpsImages.length > 0) {
    //         const latitudes = gpsImages
    //           .map(img => parseFloat(img.metadata.GPSLatitude))
    //           .filter(lat => !isNaN(lat));
    //         const longitudes = gpsImages
    //           .map(img => parseFloat(img.metadata.GPSLongitude))
    //           .filter(lon => !isNaN(lon));

    //         if (latitudes.length > 0 && longitudes.length > 0) {
    //           response.push('Geographic Coverage:');
    //           response.push(`Latitude range: ${Math.min(...latitudes).toFixed(6)} to ${Math.max(...latitudes).toFixed(6)}`);
    //           response.push(`Longitude range: ${Math.min(...longitudes).toFixed(6)} to ${Math.max(...longitudes).toFixed(6)}`);
    //           response.push('');
    //         }
    //       }

    //       // Dataset description
    //       if (dataset.description?.trim()) {
    //         response.push('Description:');
    //         response.push(dataset.description);
    //         response.push('');
    //       }

    //       response.push('Next Steps:');
    //       response.push(`Use 'smart_image_search' with dataset_slug="${dataset_slug}" to view images`);
    //       response.push('Ask about specific aspects like "thermal analysis" or "GPS coverage"');

    //       return response.join('\n');
    //     } catch (error) {
    //       return 'Error analyzing dataset: ' + (error instanceof Error ? error.message : 'Unknown error');
    //     }
    //   },
    // },

    get_quick_stats: {
      description: 'Get quick overview statistics about your thermal/RGB drone imagery database',
      parameters: z.object({
        stat_type: z.enum(['overview', 'datasets', 'thermal_rgb']).default('overview').describe('Type of statistics to retrieve'),
      }),
      execute: async ({ stat_type }) => {
        try {
          if (stat_type === 'overview') {
            // Get dataset count
            const { count: datasetCount, error: datasetError } = await supabase
              .from('datasets')
              .select('*', { count: 'exact', head: true });

            // Get total image count
            const { count: imageCount, error: imageError } = await supabase
              .from('images')
              .select('*', { count: 'exact', head: true });

            if (datasetError || imageError) {
              return 'Error fetching statistics';
            }

            const response = [
              'Quick Database Overview:',
              `Datasets: ${(datasetCount || 0).toLocaleString()}`,
              `Total images: ${(imageCount || 0).toLocaleString()}`,
              '',
              'Use "get_quick_stats" with stat_type="datasets" for detailed dataset breakdown',
            ];

            return response.join('\n');
          }

          // Add other stat types as needed...
          return `Statistics type "${stat_type}" not yet implemented`;
        } catch (error) {
          return 'Error getting statistics: ' + (error instanceof Error ? error.message : 'Unknown error');
        }
      },
    },
  };
}