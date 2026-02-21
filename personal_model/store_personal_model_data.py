import datetime
import sqlite3
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.helpers import get_closest_time_weather


BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
SCHEMA_PATH = BASE_DIR / "data" / "database" / "user_data_schema.sql"
APP_DB = BASE_DIR / "data" / "database" / "app.db"

    
def store_filter_info(user_id, filter, debug):
    if debug:
        print(f"user id: {user_id}")
        print(f"filter data: {filter}")
    
    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
    INSERT OR REPLACE INTO search_filters (
        user_id,
        min_capacity,
        max_capacity,
        tech_enhanced,
        has_printer,
        is_indoor,
        is_talking_allowed
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        filter["min_capacity"],
        filter["max_capacity"],
        filter["tech_enhanced"],
        filter["has_printer"],
        filter["is_indoor"],  
        filter["is_talking_allowed"],
    ))
    
    user_conn.commit()
    user_conn.close()

    print("user filter data inserted into user_data.db")
  

def store_study_session(user_id:str, data:dict, debug:bool):
    if debug:
        print(f"user id: {user_id}")
        print(f"data: {data}")
    
    start_time = data["started_at"]
    end_time = data["ended_at"]
    date = data["start_date"]

    session_traffic = None
    start_weather_time_local = get_closest_time_weather(start_time, date)


    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
            INSERT OR REPLACE INTO study_sessions (
                user_id,
                study_space_id,
                building_id,
                started_at,
                ended_at,
                duration_ms,
                ended_reason,
                start_date,
                start_weather_time_local,
                session_traffic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?)
        """, (
            user_id,
            data["study_space_id"],
            data["building_id"],
            data["started_at"],
            data["ended_at"],
            data["duration_ms"],
            None if "ended_reason" not in data.keys() else data["ended_reason"],
            data["start_date"],
            session_traffic,
            start_weather_time_local,
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user study session data inserted into user_data.db")    


def main():
    result = get_closest_time_weather("2026-02-09", "10:11")
    print(result)

if __name__ == "__main__":
    main()