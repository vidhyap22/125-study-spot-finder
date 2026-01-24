"""
build_index.py - Build inverted indexes for fast filter-based search
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"
INDEX_PATH = BASE_DIR / "data" / "filters_index.json"


def build_filter_indexes():
    """Build inverted indexes for all filters"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch all study spaces with their attributes
    cursor.execute("""
        SELECT 
            s.study_space_id,
            s.capacity,
            s.is_talking_allowed,
            s.must_reserve,
            s.is_indoor,
            s.tech_enhanced,
            s.building_id,
            b.has_printer,
            b.latitude,
            b.longitude
        FROM study_spaces s
        LEFT JOIN buildings b ON s.building_id = b.building_id
    """)
    
    # Initialize indexes
    indexes = {
        "capacity_ranges": defaultdict(list),  # e.g., "1-4", "5-10", "11-20", "20+"
        "talking_allowed": defaultdict(list),   # True/False
        "study_room": defaultdict(list),        # True (must_reserve) / False (public)
        "indoor": defaultdict(list),            # True/False
        "tech_enhanced": defaultdict(list),     # True/False
        "has_printer": defaultdict(list),       # True/False (building level)
        "building": defaultdict(list),          # building_id
    }
    
    for row in cursor.fetchall():
        space_id, capacity, talking, must_reserve, indoor, tech, building_id, printer, lat, lon = row
        
        # Capacity ranges
        if capacity:
            if capacity <= 4:
                indexes["capacity_ranges"]["1-4"].append(space_id)
            elif capacity <= 10:
                indexes["capacity_ranges"]["5-10"].append(space_id)
            elif capacity <= 20:
                indexes["capacity_ranges"]["11-20"].append(space_id)
            else:
                indexes["capacity_ranges"]["20+"].append(space_id)
        
        # Talking allowed
        indexes["talking_allowed"][bool(talking)].append(space_id)
        
        # Study room vs public space
        indexes["study_room"][bool(must_reserve)].append(space_id)
        
        # Indoor/outdoor
        indexes["indoor"][bool(indoor)].append(space_id)
        
        # Tech enhanced
        indexes["tech_enhanced"][bool(tech)].append(space_id)
        
        # Building has printer
        if printer is not None:
            indexes["has_printer"][bool(printer)].append(space_id)
        
        # Building
        if building_id:
            indexes["building"][building_id].append(space_id)
    
    conn.close()
    
    # Convert defaultdicts to regular dicts for JSON
    indexes = {k: dict(v) for k, v in indexes.items()}
    
    # Save to file
    with open(INDEX_PATH, 'w') as f:
        json.dump(indexes, f, indent=2)
    
    print(f"✅ Built filter indexes")
    for filter_name, filter_values in indexes.items():
        print(f"   {filter_name}: {len(filter_values)} values")
    
    return indexes


if __name__ == "__main__":
    build_filter_indexes()