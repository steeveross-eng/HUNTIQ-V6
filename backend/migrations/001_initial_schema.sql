-- Migration: 001_initial_schema.sql
-- SCENT SCIENCE™ / BIONIC™ - PostGIS Schema
-- Phase 1: Core tables for territory analysis

-- ===========================================
-- TABLE: users
-- ===========================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    plan_type VARCHAR(50) DEFAULT 'free' CHECK (plan_type IN ('free', 'premium', 'enterprise')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ===========================================
-- TABLE: cameras (trail cameras)
-- ===========================================
CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    label VARCHAR(255) NOT NULL,
    brand VARCHAR(100) CHECK (brand IN ('GardePro', 'WingHome', 'SOVACAM', 'Reconyx', 'Bushnell', 'Browning', 'autre')),
    connection_type VARCHAR(50) CHECK (connection_type IN ('ftp', 'email', 'manual')),
    ftp_host VARCHAR(255),
    ftp_username VARCHAR(255),
    ftp_password VARCHAR(255),
    ftp_path VARCHAR(500),
    email_address VARCHAR(255),
    location GEOMETRY(Point, 4326),
    connected BOOLEAN DEFAULT FALSE,
    last_seen_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cameras_user ON cameras(user_id);
CREATE INDEX idx_cameras_location ON cameras USING GIST(location);

-- ===========================================
-- TABLE: events (all observations, photos, shots)
-- ===========================================
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('gps_track', 'cache', 'camera_photo', 'tir', 'observation', 'saline', 'feeding_station')),
    species VARCHAR(50) CHECK (species IN ('orignal', 'chevreuil', 'ours', 'autre', NULL)),
    species_confidence DECIMAL(3,2) CHECK (species_confidence >= 0 AND species_confidence <= 1),
    count_estimate INTEGER DEFAULT 1,
    geom GEOMETRY(Point, 4326) NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50) DEFAULT 'app' CHECK (source IN ('app', 'camera', 'import', 'manual')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_events_user ON events(user_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_species ON events(species);
CREATE INDEX idx_events_geom ON events USING GIST(geom);
CREATE INDEX idx_events_captured ON events(captured_at DESC);

-- ===========================================
-- TABLE: camera_photos
-- ===========================================
CREATE TABLE IF NOT EXISTS camera_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID REFERENCES cameras(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    photo_path VARCHAR(500) NOT NULL,
    photo_url VARCHAR(500),
    original_filename VARCHAR(255),
    
    -- EXIF data
    exif_datetime TIMESTAMP WITH TIME ZONE,
    exif_gps_lat DECIMAL(10, 8),
    exif_gps_lon DECIMAL(11, 8),
    exif_camera_make VARCHAR(100),
    exif_camera_model VARCHAR(100),
    
    -- AI classification results
    species VARCHAR(50) CHECK (species IN ('orignal', 'chevreuil', 'ours', 'autre', NULL)),
    species_confidence DECIMAL(3,2),
    count_estimate INTEGER DEFAULT 1,
    ai_analysis_raw JSONB,
    ai_processed_at TIMESTAMP WITH TIME ZONE,
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_error TEXT,
    
    captured_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_camera_photos_user ON camera_photos(user_id);
CREATE INDEX idx_camera_photos_camera ON camera_photos(camera_id);
CREATE INDEX idx_camera_photos_event ON camera_photos(event_id);
CREATE INDEX idx_camera_photos_status ON camera_photos(processing_status);
CREATE INDEX idx_camera_photos_species ON camera_photos(species);

-- ===========================================
-- TABLE: layers_heatmap_activite
-- ===========================================
CREATE TABLE IF NOT EXISTS layers_heatmap_activite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    species VARCHAR(50) CHECK (species IN ('orignal', 'chevreuil', 'ours', 'all', NULL)),
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    intensity DECIMAL(5,4) CHECK (intensity >= 0 AND intensity <= 1),
    event_count INTEGER DEFAULT 0,
    time_window_hours INTEGER DEFAULT 72,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_heatmap_user ON layers_heatmap_activite(user_id);
CREATE INDEX idx_heatmap_species ON layers_heatmap_activite(species);
CREATE INDEX idx_heatmap_geom ON layers_heatmap_activite USING GIST(geom);

-- ===========================================
-- TABLE: layers_prob_presence
-- ===========================================
CREATE TABLE IF NOT EXISTS layers_prob_presence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    species VARCHAR(50) NOT NULL CHECK (species IN ('orignal', 'chevreuil', 'ours')),
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    probability DECIMAL(3,2) CHECK (probability >= 0 AND probability <= 1),
    time_period VARCHAR(20) CHECK (time_period IN ('matin', 'jour', 'soir', 'nuit', 'all')),
    factors JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_prob_user ON layers_prob_presence(user_id);
CREATE INDEX idx_prob_species ON layers_prob_presence(species);
CREATE INDEX idx_prob_geom ON layers_prob_presence USING GIST(geom);

-- ===========================================
-- TABLE: layers_zones_refuge
-- ===========================================
CREATE TABLE IF NOT EXISTS layers_zones_refuge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    species VARCHAR(50) CHECK (species IN ('orignal', 'chevreuil', 'ours', 'all', NULL)),
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    refuge_score DECIMAL(3,2) CHECK (refuge_score >= 0 AND refuge_score <= 1),
    factors JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_refuge_user ON layers_zones_refuge(user_id);
CREATE INDEX idx_refuge_species ON layers_zones_refuge(species);
CREATE INDEX idx_refuge_geom ON layers_zones_refuge USING GIST(geom);

-- ===========================================
-- TABLE: layers_acces (roads, water, fields)
-- ===========================================
CREATE TABLE IF NOT EXISTS layers_acces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    layer_type VARCHAR(50) NOT NULL CHECK (layer_type IN ('chemin', 'champ', 'eau', 'ravage', 'coupe', 'friche')),
    name VARCHAR(255),
    geom GEOMETRY(Geometry, 4326) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_acces_user ON layers_acces(user_id);
CREATE INDEX idx_acces_type ON layers_acces(layer_type);
CREATE INDEX idx_acces_geom ON layers_acces USING GIST(geom);

-- ===========================================
-- TABLE: analysis_jobs (background processing queue)
-- ===========================================
CREATE TABLE IF NOT EXISTS analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('ia_classification', 'heatmap_update', 'prob_calculation', 'refuge_calculation')),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    priority INTEGER DEFAULT 5,
    payload JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_jobs_type ON analysis_jobs(job_type);
CREATE INDEX idx_jobs_priority ON analysis_jobs(priority DESC, created_at ASC);

-- ===========================================
-- FUNCTION: Update timestamp trigger
-- ===========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- MATERIALIZED VIEW: Recent activity heatmap
-- ===========================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_recent_activity AS
SELECT 
    e.user_id,
    e.species,
    ST_SnapToGrid(e.geom, 0.001) as grid_cell,
    COUNT(*) as event_count,
    MAX(e.captured_at) as last_activity
FROM events e
WHERE e.captured_at > NOW() - INTERVAL '7 days'
GROUP BY e.user_id, e.species, ST_SnapToGrid(e.geom, 0.001);

CREATE UNIQUE INDEX idx_mv_recent_activity ON mv_recent_activity(user_id, species, grid_cell);

-- Grant permissions to bionic user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bionic;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bionic;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO bionic;
