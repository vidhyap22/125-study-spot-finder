import sqlite3
import requests
from pathlib import Path


url = "https://anteaterapi.com/v2/rest/libraryTraffic"
params = [{"libraryName": "Langson Library"}, {"libraryName": "Science Library"}, {"libraryName": "Gateway Study Center"}]

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"

class LibraryTraffic:
    def __init__(self, url, params, DB_PATH):
        self.url = url
        self.params = params
        self.DB_PATH = DB_PATH

    def get_building_id(self, cursor, library_name):
        #get the building id from library name
        cursor.execute(
            "SELECT building_id FROM buildings WHERE name = ?",
            (library_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def clear_library_database(self, cursor):
        cursor.execute("DELETE FROM library_traffic;")

    def insert_library_traffic_data(self, cursor, data):
        building_id = self.get_building_id(cursor, data["libraryName"])
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


    def update_database(self):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        self.clear_library_database(cursor)
        for param in params:
            resp = requests.get(url, params=param, timeout=15)
            resp.raise_for_status()

            payload = resp.json()
            for item in payload.get("data", []):
                self.insert_library_traffic_data(cursor, item)

        conn.commit()
        conn.close()

def main():
    library_traffic = LibraryTraffic(url, params,DB_PATH)
    library_traffic.update_database()
    """
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
    """
if __name__ == "__main__":
    main()