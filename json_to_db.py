"""
json_to_db.py is responsible for... 
    * Parsing through data/scraped_info/room_info JSON files and inserting the study space information into the 'study_spaces' table.
    * Parsing through data/scraped_info/buildings.json to insert building information into the 'buildings' table.
SQLite database is located at data/database/app.db. 
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOM_DATA_DIR = BASE_DIR / "data" / "scraped_info" / "room_info"
BUILDINGS_DATA_DIR = BASE_DIR / "data" / "scraped_info"
DB_PATH = BASE_DIR / "data" / "database" / "app.db"

ROOMS_JSON = [
    ROOM_DATA_DIR / "ALP_room_info.json", 
    ROOM_DATA_DIR / "Gateway_room_info.json",
    ROOM_DATA_DIR / "Langson_room_info.json",
    ROOM_DATA_DIR / "Multimedia_room_info.json",
    ROOM_DATA_DIR / "Science_room_info.json",
]

BUILDINGS_JSON = BUILDINGS_DATA_DIR / "buildings_info.json"

def bool_to_int(value):
    """Convert Python boolean or None to SQLite-friendly int"""
    if value is None:
        return None
    return 1 if value else 0


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_buildings(cursor, buildings_dict):
    """Insert buildings from JSON dict where keys are building_ids"""
    for building_id, building_data in buildings_dict.items():
        cursor.execute("""
            INSERT OR REPLACE INTO buildings (
                building_id,
                name,
                has_printer,
                opening_time,
                closing_time,
                longitude,
                latitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            building_id,
            building_data["name"],
            bool_to_int(building_data.get("has_printer")),
            building_data.get("opening_time"),
            building_data.get("closing_time"),
            building_data.get("longitude"),
            building_data.get("latitude")
        ))

def insert_study_spaces(cursor, rooms):
    for r in rooms:
        cursor.execute("""
            INSERT OR REPLACE INTO study_spaces (
                study_space_id,
                name,
                capacity,
                must_reserve,
                tech_enhanced,
                is_indoor,
                is_talking_allowed,
                building_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"],
            r["name"],
            r.get("capacity"),
            bool_to_int(r.get("must_reserve")),
            bool_to_int(r.get("tech_enhanced")),
            bool_to_int(r.get("is_indoor")),
            bool_to_int(r.get("is_talking_allowed")),
            r.get("building_id")
        ))


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🗄️  Populating database...")
    print(f'Inserting buildings...')
    buildings = load_json(BUILDINGS_JSON)
    insert_buildings(cursor, buildings)
    print(f"✅ Inserted {len(buildings)} buildings")
    
    print(f'Inserting study rooms...')
    for json_file in ROOMS_JSON:
        rooms = load_json(json_file)
        insert_study_spaces(cursor, rooms)
        print(f"✅ Inserted {len(rooms)} study spaces from {json_file.name}")

    print("🗄️  Done populating database...")

    conn.commit()
    conn.close()

    print("✅ Database populated successfully")


if __name__ == "__main__":
    main()