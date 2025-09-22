// Database context content for LLM SQL generation
export const DATABASE_CONTEXT = `# Kavion Thermal/RGB Database Context for LLM SQL Generation

## Database Overview
This is a PostgreSQL database for a thermal and RGB drone imagery analysis platform called Kavion. The database stores datasets, images, annotations, gas readings, and user management data for industrial inspection and analysis workflows.

## Core Business Domain
- **Primary Use Case**: Industrial thermal and RGB drone imagery analysis
- **Key Entities**: Datasets, Images, Annotations, Gas Readings, Organizations, Users
- **Data Types**: Thermal imagery, RGB imagery, gas sensor readings, 3D Gaussian splats, geographic data

## Table Structure and Relationships

### 1. Core Data Tables

#### \`datasets\` (Primary Entity)
**Purpose**: Central entity storing information about drone imagery datasets
**Key Fields**:
- \`id\` (uuid, PK): Unique dataset identifier
- \`name\` (text): Human-readable dataset name (e.g., "Valero Sim", "Wacker 2024")
- \`description\` (text): Optional description
- \`slug\` (text, UNIQUE): URL-friendly identifier
- \`organization_id\` (uuid): Links to organization
- \`owner_id\` (uuid): Dataset owner
- \`visibility\` (text): "private", "organization", "public"
- \`provider\` (text): Storage provider (e.g., "azure")
- \`storage_path\` (text): Path to dataset files
- \`grouping_status\` (text): "pending", "completed", etc.
- \`gaussian_splats\` (jsonb): 3D reconstruction data
- \`reference_latitude/longitude/altitude\` (double precision): Geographic reference point
- \`cover_image_id\` (uuid): Thumbnail image
- \`reference_image_id\` (uuid): Reference image for alignment

**Sample Data**:
- "Valero Sim" (organization visibility, azure provider)
- "Torrance 2023" (Inspection dataset)
- "Wacker 2024" (organization visibility)

#### \`images\` (Core Entity)
**Purpose**: Individual images within datasets
**Key Fields**:
- \`id\` (uuid, PK): Unique image identifier
- \`dataset_id\` (uuid): Links to parent dataset
- \`filename\` (text): Original filename with path
- \`storage_path\` (text): Full storage path
- \`metadata\` (jsonb): EXIF and image metadata
- \`tags\` (text[]): Array of tags
- \`thumbnail_url\` (text): Thumbnail URL
- \`data_group_id\` (uuid): Links to data groups
- \`grouping_status\` (text): "pending", "completed", etc.
- \`geom\` (geometry): 2D geographic location
- \`geom_3d\` (geometry): 3D geographic location

**Sample Data**:
- "TRC-090122-3/S1003632.JPG" (from Torrance 2023)
- "DJI_202408071955_004/DJI_20240807200020_0080_V.JPG" (thermal imagery)

#### \`annotations\` (Analysis Results)
**Purpose**: AI-generated annotations and analysis results
**Key Fields**:
- \`id\` (uuid, PK): Unique annotation identifier
- \`coco_annotation_id\` (integer): COCO format annotation ID
- \`existing_image_id\` (uuid): Links to image
- \`category_id\` (uuid): Links to annotation category
- \`bbox\` (jsonb): Bounding box coordinates
- \`area\` (double precision): Annotation area

#### \`annotation_categories\` (Classification System)
**Purpose**: Hierarchical classification system for annotations
**Key Fields**:
- \`id\` (uuid, PK): Unique category identifier
- \`coco_category_id\` (integer, UNIQUE): COCO format category ID
- \`name\` (text): Category name
- \`parent_category\` (text): Parent category
- \`subcategory\` (text): Subcategory

**Sample Categories**:
- "Anomalies/Crack Detection"
- "Thermal Imaging/Thermal Leakage"
- "Thermal Imaging/Hot Spots"
- "Leakage and Fouling/Leaks"
- "Fasteners and Components/Fastener Issues"

### 2. Sensor Data Tables

#### \`gas_readings\` (Environmental Data)
**Purpose**: Gas sensor readings from drone flights
**Key Fields**:
- \`id\` (uuid, PK): Unique reading identifier
- \`time_stamp\` (timestamp): Reading timestamp
- \`abs_alt_m\` (numeric): Absolute altitude in meters
- \`longitude/latitude\` (numeric): GPS coordinates
- \`temperature_c\` (numeric): Temperature in Celsius
- \`humidity_percent\` (numeric): Humidity percentage
- \`pressure_pa\` (numeric): Atmospheric pressure
- \`no2_ug_m3\` (numeric): NO2 concentration
- \`hcl_mg_m3\` (numeric): HCL concentration
- \`h2_percent\` (numeric): Hydrogen percentage
- \`cl2_mg_m3\` (numeric): Chlorine concentration
- \`serial_no\` (varchar): Sensor serial number
- \`location\` (varchar): Location description
- \`geom\` (geometry): 2D geographic location
- \`geom_3d\` (geometry): 3D geographic location

**Sample Data**:
- Temperature: ~19°C, Humidity: ~54%, NO2: ~28 μg/m³
- Timestamps: 2024-08-19T21:56:20+00:00

### 3. 3D Reconstruction Data

#### \`gaussian_splat_files\` (3D Data)
**Purpose**: 3D Gaussian splat reconstruction files
**Key Fields**:
- \`id\` (uuid, PK): Unique file identifier
- \`dataset_id\` (uuid): Links to dataset
- \`filename\` (text): Splat file name
- \`storage_path\` (text): File storage path
- \`file_size\` (bigint): File size in bytes
- \`format\` (text): File format
- \`metadata\` (jsonb): File metadata

#### \`data_groups\` (Image Grouping)
**Purpose**: Groups related images (e.g., RGB-thermal pairs)
**Key Fields**:
- \`id\` (uuid, PK): Unique group identifier
- \`dataset_id\` (uuid): Links to dataset
- \`type\` (text): Group type (e.g., "rgb_thermal_pair")
- \`metadata\` (jsonb): Group metadata

### 4. User Management Tables

#### \`organizations\` (Multi-tenancy)
**Purpose**: Organization/company management
**Key Fields**:
- \`id\` (uuid, PK): Unique organization identifier
- \`name\` (text): Organization name
- \`created_at/updated_at\` (timestamp): Timestamps

#### \`profiles\` (User Profiles)
**Purpose**: User profile information
**Key Fields**:
- \`id\` (uuid, PK): Unique user identifier
- \`email\` (text): User email
- \`full_name\` (text): User's full name
- \`created_at/updated_at\` (timestamp): Timestamps

#### \`organization_members\` (User-Organization Links)
**Purpose**: Links users to organizations with roles
**Key Fields**:
- \`id\` (uuid, PK): Unique membership identifier
- \`organization_id\` (uuid): Links to organization
- \`user_id\` (uuid): Links to user profile
- \`role\` (text): User role in organization
- \`created_at/updated_at\` (timestamp): Timestamps

### 5. Chat/Communication Tables

#### \`chat_sessions\` (Chat Sessions)
**Purpose**: Chat session management
**Key Fields**:
- \`id\` (uuid, PK): Unique session identifier
- \`user_id\` (uuid): Session owner
- \`title\` (text): Session title (default: "New Chat")
- \`created_at/updated_at\` (timestamp): Timestamps

#### \`messages\` (Chat Messages)
**Purpose**: Individual chat messages
**Key Fields**:
- \`id\` (uuid, PK): Unique message identifier
- \`session_id\` (uuid): Links to chat session
- \`topic\` (text): Message topic
- \`user_id\` (uuid): Message author
- \`content\` (text): Message content
- \`extension\` (text): Message extension type
- \`payload\` (jsonb): Additional message data
- \`is_user\` (boolean): Whether message is from user
- \`event\` (text): Event type
- \`private\` (boolean): Whether message is private
- \`created_at/updated_at/inserted_at\` (timestamp): Timestamps

### 6. COCO Integration Tables

#### \`coco_image_mappings\` (COCO Format Support)
**Purpose**: Maps internal images to COCO format
**Key Fields**:
- \`id\` (uuid, PK): Unique mapping identifier
- \`coco_image_id\` (integer): COCO format image ID
- \`existing_image_id\` (uuid, UNIQUE): Links to internal image
- \`coco_metadata\` (jsonb): COCO-specific metadata

#### \`coco_category_mapping\` (View)
**Purpose**: View mapping COCO categories to internal categories
**Key Fields**:
- \`supabase_category_uuid\` (uuid): Internal category ID
- \`category_name\` (text): Category name
- \`coco_category_id\` (integer): COCO category ID

## Key Relationships and Patterns

### Primary Relationships
1. **datasets** → **images** (one-to-many via \`dataset_id\`)
2. **images** → **annotations** (one-to-many via \`existing_image_id\`)
3. **annotation_categories** → **annotations** (one-to-many via \`category_id\`)
4. **datasets** → **data_groups** (one-to-many via \`dataset_id\`)
5. **data_groups** → **images** (one-to-many via \`data_group_id\`)
6. **organizations** → **datasets** (one-to-many via \`organization_id\`)
7. **profiles** → **datasets** (one-to-many via \`owner_id\`)
8. **organizations** → **organization_members** (one-to-many via \`organization_id\`)
9. **profiles** → **organization_members** (one-to-many via \`user_id\`)
10. **chat_sessions** → **messages** (one-to-many via \`session_id\`)

### Geographic Data
- **images**: \`geom\` (2D), \`geom_3d\` (3D) - PostGIS geometry columns
- **gas_readings**: \`geom\` (2D), \`geom_3d\` (3D) - PostGIS geometry columns
- **datasets**: \`reference_latitude/longitude/altitude\` - Reference coordinates

### JSONB Fields (Query with -> and ->> operators)
- **datasets**: \`gaussian_splats\`, \`default_camera\`, \`offsets\`, \`credentials\`
- **images**: \`metadata\` (EXIF data)
- **annotations**: \`bbox\` (bounding box coordinates)
- **data_groups**: \`metadata\`
- **gas_readings**: Various sensor readings
- **messages**: \`payload\`
- **coco_image_mappings**: \`coco_metadata\`

## Common Query Patterns

### 1. Dataset Queries
\`\`\`sql
-- List all datasets
SELECT id, name, description, visibility, provider, created_at FROM datasets;

-- Find datasets by name pattern
SELECT * FROM datasets WHERE name ILIKE '%valero%';

-- Get dataset with image count
SELECT d.*, COUNT(i.id) as image_count 
FROM datasets d 
LEFT JOIN images i ON d.id = i.dataset_id 
GROUP BY d.id;
\`\`\`

### 2. Image Queries
\`\`\`sql
-- Get images from specific dataset
SELECT * FROM images WHERE dataset_id = 'dataset-uuid';

-- Find images by filename pattern
SELECT * FROM images WHERE filename ILIKE '%thermal%';

-- Get images with metadata
SELECT filename, metadata->>'DateTime' as capture_time 
FROM images 
WHERE metadata->>'DateTime' IS NOT NULL;
\`\`\`

### 3. Annotation Queries
\`\`\`sql
-- Get annotations for specific image
SELECT a.*, ac.name as category_name 
FROM annotations a 
JOIN annotation_categories ac ON a.category_id = ac.id 
WHERE a.existing_image_id = 'image-uuid';

-- Count annotations by category
SELECT ac.name, COUNT(*) as count 
FROM annotations a 
JOIN annotation_categories ac ON a.category_id = ac.id 
GROUP BY ac.name;
\`\`\`

### 4. Geographic Queries
\`\`\`sql
-- Find images within geographic bounds
SELECT * FROM images 
WHERE ST_Within(geom, ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326));

-- Get gas readings near specific location
SELECT * FROM gas_readings 
WHERE ST_DWithin(geom, ST_Point(longitude, latitude), 1000);
\`\`\`

### 5. Time-based Queries
\`\`\`sql
-- Get recent datasets
SELECT * FROM datasets 
WHERE created_at > NOW() - INTERVAL '30 days';

-- Get gas readings for specific time range
SELECT * FROM gas_readings 
WHERE time_stamp BETWEEN '2024-08-19' AND '2024-08-20';
\`\`\`

## Important Indexes for Performance

### Primary Indexes
- All tables have primary key indexes on \`id\`
- \`datasets.slug\` has unique index
- \`annotation_categories.coco_category_id\` has unique index

### Foreign Key Indexes
- \`images.dataset_id\` - for dataset-image joins
- \`annotations.existing_image_id\` - for image-annotation joins
- \`annotations.category_id\` - for category-annotation joins
- \`data_groups.dataset_id\` - for dataset-group joins
- \`images.data_group_id\` - for group-image joins

### Geographic Indexes
- \`images.geom\` and \`images.geom_3d\` - GIST indexes for spatial queries
- \`gas_readings.geom\` and \`gas_readings.geom_3d\` - GIST indexes for spatial queries
- \`gas_readings.coordinates\` - B-tree index on longitude, latitude

### Metadata Indexes
- \`images.metadata\` - indexes on DateTime, DateTimeOriginal, DateTimeDigitized
- \`datasets.gaussian_splats\` - GIN index for JSONB queries

## Data Types and Constraints

### UUID Usage
- All primary keys are UUIDs
- All foreign keys are UUIDs
- Use \`gen_random_uuid()\` for new records

### Timestamps
- Most tables have \`created_at\` and \`updated_at\` timestamps
- Use \`now()\` as default for timestamps
- Timezone-aware timestamps (\`timestamp with time zone\`)

### JSONB Fields
- Use \`->\` for JSON object access
- Use \`->>\` for JSON text extraction
- Use \`@>\` for JSON containment
- Use \`?\` for key existence

### Arrays
- \`images.tags\` is a text array
- Use \`ANY()\` for array element queries
- Use \`@>\` for array containment

## Common Business Queries

### Dataset Management
\`\`\`sql
-- Get dataset statistics
SELECT 
    d.name,
    COUNT(i.id) as image_count,
    COUNT(DISTINCT a.id) as annotation_count,
    d.created_at
FROM datasets d
LEFT JOIN images i ON d.id = i.dataset_id
LEFT JOIN annotations a ON i.id = a.existing_image_id
GROUP BY d.id, d.name, d.created_at;

-- Find datasets with 3D content
SELECT * FROM datasets 
WHERE gaussian_splats IS NOT NULL;
\`\`\`

### Image Analysis
\`\`\`sql
-- Get images with annotations
SELECT 
    i.filename,
    COUNT(a.id) as annotation_count,
    STRING_AGG(ac.name, ', ') as categories
FROM images i
LEFT JOIN annotations a ON i.id = a.existing_image_id
LEFT JOIN annotation_categories ac ON a.category_id = ac.id
GROUP BY i.id, i.filename;

-- Find thermal images
SELECT * FROM images 
WHERE filename ILIKE '%thermal%' OR filename ILIKE '%_V.JPG';
\`\`\`

### Gas Sensor Analysis
\`\`\`sql
-- Get gas reading statistics
SELECT 
    AVG(temperature_c) as avg_temp,
    AVG(humidity_percent) as avg_humidity,
    AVG(no2_ug_m3) as avg_no2,
    COUNT(*) as reading_count
FROM gas_readings
WHERE time_stamp > NOW() - INTERVAL '24 hours';

-- Find high NO2 readings
SELECT * FROM gas_readings 
WHERE no2_ug_m3 > 50 
ORDER BY time_stamp DESC;
\`\`\`

## Security and Access Patterns

### Visibility Levels
- \`private\`: Only owner can access
- \`organization\`: Organization members can access
- \`public\`: Anyone can access

### User Context
- Always consider user permissions when querying
- Use \`owner_id\` and \`organization_id\` for access control
- Check \`organization_members\` for user-organization relationships

## Performance Considerations

### Large Tables
- \`images\` table likely contains thousands of records
- \`gas_readings\` table contains time-series data
- Use appropriate indexes and LIMIT clauses

### JSONB Queries
- Index frequently queried JSONB fields
- Use GIN indexes for JSONB containment queries
- Consider extracting frequently used fields to separate columns

### Geographic Queries
- Use PostGIS functions for spatial queries
- Consider spatial indexes for large geographic datasets
- Use appropriate coordinate reference systems

## Error Handling

### Common Issues
- UUID format validation
- JSONB field access (use proper operators)
- Geographic coordinate validation
- Timestamp timezone handling

### Best Practices
- Always use parameterized queries
- Validate UUIDs before querying
- Handle NULL values in JSONB fields
- Use appropriate data types for numeric fields

This context provides comprehensive information for generating accurate SQL queries for the Kavion thermal/RGB drone imagery analysis database.`;
