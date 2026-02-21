import sqlite3
import requests
from pathlib import Path


url = "https://anteaterapi.com/v2/rest/libraryTraffic"
params = [{"libraryName": "Langson Library"}, {"libraryName": "Science Library"}, {"libraryName": "Gateway Study Center"}]

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"


def get_building_id(cursor, library_name):
    #get the building id from library name
    cursor.execute(
        "SELECT building_id FROM buildings WHERE name = ?",
        (library_name,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def insert_library_traffic_data(cursor, data):
    
    building_id = get_building_id(cursor, data["libraryName"])
    cursor.execute("""
        INSERT INTO library_traffic (
            building_id,
            location_name,
            traffic_count,
            traffic_percentage,
            timestamp
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        building_id,        
        data["locationName"],
        data["trafficCount"],
        data["trafficPercentage"],
        data["timestamp"]
    ))

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for param in params:
        resp = requests.get(url, params=param, timeout=15)
        resp.raise_for_status()

        payload = resp.json()
        for item in payload.get("data", []):
            insert_library_traffic_data(cursor, item)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()