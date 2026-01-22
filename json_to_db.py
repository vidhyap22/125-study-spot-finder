"""
json_to_db.py is responsible for parsing through data/scraped_info/room_info JSON files and inserting the study space information into the study_spaces table in the SQLite database located at data/database/app.db.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "scraped_info" / "room_info"
DB_PATH = BASE_DIR / "data" / "database" / "app.db"

ROOMS_JSON = [
    DATA_DIR / "ALP_room_info.json", 
    DATA_DIR / "Gateway_room_info.json",
    DATA_DIR / "Langson_room_info.json",
    DATA_DIR / "Multimedia_room_info.json",
    DATA_DIR / "Science_room_info.json",
]


def bool_to_int(value):
    """Convert Python boolean or None to SQLite-friendly int"""
    if value is None:
        return None
    return 1 if value else 0


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    for json_file in ROOMS_JSON:
        print(f"Processing {json_file.name}...")
        rooms = load_json(json_file)
        insert_study_spaces(cursor, rooms)

    conn.commit()
    conn.close()

    print("✅ Database populated successfully")


if __name__ == "__main__":
    main()