-- Drop existing tables if they exist
DROP TABLE IF EXISTS study_spaces;
DROP TABLE IF EXISTS buildings;
DROP TABLE IF EXISTS library_traffic;

-- Create Building/Location Table 
CREATE TABLE buildings (
  building_id TEXT PRIMARY KEY,        
  name TEXT NOT NULL,
  has_printer INTEGER, 
  opening_time TEXT,
  closing_time TEXT,
  longitude REAL,
  latitude REAL
);

-- Create Study Spaces Table
CREATE TABLE study_spaces (
  study_space_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  capacity INTEGER,
  must_reserve INTEGER,
  tech_enhanced INTEGER,
  is_indoor INTEGER,
  is_talking_allowed INTEGER,
  building_id TEXT,
  FOREIGN KEY (building_id) REFERENCES buildings(building_id)
);

-- Create library traffic table
CREATE TABLE library_traffic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id TEXT,
    location_name TEXT,
    traffic_count INTEGER,
    traffic_percentage REAL,
    timestamp TEXT,
    FOREIGN KEY (building_id) REFERENCES buildings(building_id)
);
