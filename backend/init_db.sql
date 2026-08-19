-- 1. Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- 2. Create Core Tables
CREATE TABLE user_profiles (
user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
organization_name VARCHAR(255) NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE runoff_coefficients (
material_key VARCHAR(50) PRIMARY KEY,
display_name VARCHAR(100) NOT NULL,
coefficient_value NUMERIC(3,2) NOT NULL CHECK (coefficient_value BETWEEN
0.0 AND 1.0),
initial_abstraction_mm NUMERIC(4,2) NOT NULL -- Upgraded for SCS-CN model
);
CREATE TABLE assessment_sites (
site_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
site_name VARCHAR(255) NOT NULL,
roof_material_key VARCHAR(50) REFERENCES runoff_coefficients(material_key),
roof_geometry GEOMETRY(Polygon, 4326) NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT valid_geometry CHECK (ST_IsValid(roof_geometry))
);
CREATE TABLE regional_weather_stations (
station_id SERIAL PRIMARY KEY,
location GEOMETRY(Point, 4326) NOT NULL,
annual_rainfall_mm NUMERIC(6,2) NOT NULL,
peak_hourly_intensity_mm NUMERIC(5,2) NOT NULL
);
CREATE TABLE hydrogeological_profiles (
profile_id SERIAL PRIMARY KEY,
boundary_polygon GEOMETRY(Polygon, 4326) NOT NULL,
soil_infiltration_rate_mm_hr NUMERIC(5,2) NOT NULL,
water_table_depth_meters NUMERIC(5,2) NOT NULL
);
-- 3. Apply Spatial Indices for Query Performance
CREATE INDEX idx_assessment_geom ON assessment_sites USING GIST(roof_geometry);
CREATE INDEX idx_weather_stations_geom ON regional_weather_stations USING
GIST(location);
CREATE INDEX idx_hydrogeo_geom ON hydrogeological_profiles USING
GIST(boundary_polygon);
-- 4. Enterprise Security: Row Level Security (RLS)
ALTER TABLE assessment_sites ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_site_access ON assessment_sites
FOR ALL
USING (user_id = current_setting('app.current_user_id')::UUID);
-- 5. Seed Base Data
INSERT INTO runoff_coefficients (material_key, display_name, coefficient_value,
initial_abstraction_mm) VALUES
('concrete', 'Reinforced Cement Concrete (RCC)', 0.85, 2.5),
('corrugated_metal', 'Corrugated Galvanized Iron', 0.90, 1.5),
('clay_tile', 'Clay Tiles Surface', 0.80, 3.0),
('asbestos', 'Asbestos Cement Sheets', 0.75, 2.0);
-- Mock Weather Station Data for Interpolation Testing (Kolkata/Howrah Region)
INSERT INTO regional_weather_stations (location, annual_rainfall_mm,
peak_hourly_intensity_mm) VALUES
(ST_SetSRID(ST_MakePoint(88.3639, 22.5726), 4326), 1600.0, 45.0),
(ST_SetSRID(ST_MakePoint(88.3215, 22.5855), 4326), 1580.0, 42.0),
(ST_SetSRID(ST_MakePoint(88.2636, 22.5958), 4326), 1620.0, 48.0);
