import datetime
import sqlite3
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.helpers import get_closest_time_weather, get_library_traffic, round_to_nearest_hour

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
    start_date = data["start_date"]
    end_date = data["end_date"]
    
    session_traffic = get_library_traffic(data["building_id"], data["study_space_id"], start_time, end_time, start_date, end_date)

    start_weather_time_local = get_closest_time_weather(start_date, start_time)

    if debug:
        print(f"traffic: {session_traffic}")
        print(f"weather: {start_weather_time_local}")

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
                end_date,
                start_weather_time_local,
                session_traffic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
        """, (
            user_id,
            data["study_space_id"],
            data["building_id"],
            data["started_at"],
            data["ended_at"],
            data["duration_ms"],
            None if "ended_reason" not in data.keys() else data["ended_reason"],
            data["start_date"],
            data["end_date"],
            start_weather_time_local,
            session_traffic
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user study session data inserted into user_data.db")    


def store_bookmarks(user_id, data, debug):
    if debug:
        print(f"user_id: {user_id}")
        print(f"data: {data}")

    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
        INSERT OR REPLACE INTO bookmarks (
            user_id,
            study_space_id,
            building_id,
            created_at
        ) VALUES (?,?,?,?)
        """, (
            user_id,
            data["study_space_id"],
            data["building_id"],
            data["created_at"]
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user bookmarks data inserted into user_data.db") 

def delete_bookmarks(user_id, data, debug):
    if debug:
        print(f"user_id: {user_id}")
        print(f"data: {data}")

    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
        DELETE FROM bookmarks
        WHERE user_id = ? AND study_space_id = ?
        """, (
            user_id,
            data["study_space_id"]
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user bookmarks data deleted from user_data.db") 


def store_spot_view(user_id, data, debug):
    if debug:
        print(f"user_id: {user_id}")
        print(f"data: {data}")

    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
        INSERT OR REPLACE INTO spot_detail_views (
            user_id,
            study_space_id,
            building_id,
            opened_at,
            closed_at,
            dwell_ms,
            source,
            list_rank                    
        ) VALUES (?,?,?,?,?,?,?,?)
        """, (
            user_id,
            data["study_space_id"],
            data["building_id"],
            data["opened_at"],
            data["closed_at"],
            data["dwell_ms"],
            data["source"] if "source" in data.keys() else None,
            data["list_rank"] if "list_rank" in data.keys() else None
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user bookmarks data inserted into user_data.db") 


def store_spot_feedback(user_id, data, debug):
    if debug:
        print(f"user_id: {user_id}")
        print(f"data: {data}")

    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
        INSERT OR REPLACE INTO spot_feedback(
            user_id,
            study_space_id,
            building_id,
            rating,
            updated_at              
        ) VALUES (?,?,?,?,?)
        """, (
            user_id,
            data["study_space_id"],
            data["building_id"],
            data["rating"],
            data["updated_at"]
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user spot feedback data inserted into user_data.db") 


def add_user(user_id, data, debug):
    if debug:
        print(f"user_id: {user_id}")
        print(f"data: {data}")
    

    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    user_cur.execute("""
        INSERT INTO users (
            user_id,
            created_at      
        ) VALUES (?,?)
        """, (
            user_id,
            data["created_at"],
        ))
    
    user_conn.commit()
    user_conn.close()

    print("user inserted into user_data.db") 




def main():
    result = get_closest_time_weather("2026-02-09", "10:11")
    print(result)

if __name__ == "__main__":
    main()