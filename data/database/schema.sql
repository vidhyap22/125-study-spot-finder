CREATE TABLE buildings (
  building_id TEXT PRIMARY KEY,        
  name TEXT NOT NULL,
  has_printer INTEGER, 
  opening_time TEXT,
  closing_time TEXT,
  longitude REAL,
  latitude REAL
);

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