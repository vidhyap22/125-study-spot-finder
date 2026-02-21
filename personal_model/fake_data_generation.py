import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
APP_DB = BASE_DIR / "data" / "database" / "app.db"
SCHEMA_PATH = BASE_DIR / "data" / "database" / "user_data_schema.sql"



def clear_spot_feedback(cursor):
    cursor.execute("DELETE FROM spot_feedback;")

def main():


    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()


    users = [
        {
            "user_id": "USER_001",
            "created_at": "2026-01-10 09:00:00",
        },
        {
            "user_id": "USER_002",
            "created_at": "2026-01-15 14:30:00",
        },
    ]

    study_sessions = [
        {
            "session_id": "sess_001",
            "user_id": "USER_001",
            "study_space_id": 44672,
            "building_id": "SLIB",
            "started_at": "2026-02-05 18:30:00",
            "ended_at": "2026-02-05 20:00:00",
            "duration_ms": 5400000,
            "ended_reason": "user_end",
            "start_date": "2026-02-05",
            "start_weather_time_local": "Fog",
            "session_traffic": 0.32,
        },
        {
            "session_id": "sess_002",
            "user_id": "USER_002",
            "study_space_id": 34681,
            "building_id": "ALP",
            "started_at": "2026-02-06 19:00:00",
            "ended_at": "2026-02-06 20:15:00",
            "duration_ms": 4500000,
            "ended_reason": "app_background",
            "start_date": "2026-02-06",
            "start_weather_time_local": "Clear",
            "session_traffic": 0.55,
        },
        {
            "session_id": "sess_003",
            "user_id": "USER_001",
            "study_space_id": 44672,
            "building_id": "SLIB",
            "started_at": "2026-02-07 14:30:00",
            "ended_at": "2026-02-07 16:10:00",
            "duration_ms": 6000000,
            "ended_reason": "user_exit",
            "start_date": "2026-02-07",
            "start_weather_time_local": "Rain",
            "session_traffic": 0.70,
        },
        {
            "session_id": "sess_004",
            "user_id": "USER_002",
            "study_space_id": 34681,
            "building_id": "ALP",
            "started_at": "2026-02-07 18:40:00",
            "ended_at": "2026-02-07 19:05:00",
            "duration_ms": 1500000,
            "ended_reason": "app_background",
            "start_date": "2026-02-07",
            "start_weather_time_local": "Clear",
            "session_traffic": 0.38,
        },
        {
            "session_id": "sess_005",
            "user_id": "USER_001",
            "study_space_id": 44704,
            "building_id": "GSC",
            "started_at": "2026-02-08 09:10:00",
            "ended_at": None,
            "duration_ms": None,
            "ended_reason": None,
            "start_date": "2026-02-08",
            "start_weather_time_local": "Fog",
            "session_traffic": 0.05,
        },
        {
            "session_id": "sess_006",
            "user_id": "USER_001",
            "study_space_id": 44668,
            "building_id": "SLIB",
            "started_at": "2026-02-08 13:20:00",
            "ended_at": "2026-02-08 14:05:00",
            "duration_ms": 2700000,
            "ended_reason": "user_exit",
            "start_date": "2026-02-08",
            "start_weather_time_local": "Partly Cloudy",
            "session_traffic": 0.43,
        },
        {
            "session_id": "sess_007",
            "user_id": "USER_002",
            "study_space_id": 44706,
            "building_id": "GSC",
            "started_at": "2026-02-08 17:50:00",
            "ended_at": "2026-02-08 18:10:00",
            "duration_ms": 1200000,
            "ended_reason": "noise",
            "start_date": "2026-02-08",
            "start_weather_time_local": "Clear",
            "session_traffic": 0.33,
        },
        {
            "session_id": "sess_008",
            "user_id": "USER_001",
            "study_space_id": 155343,
            "building_id": "LLIB",
            "started_at": "2026-02-09 09:30:00",
            "ended_at": "2026-02-09 11:00:00",
            "duration_ms": 5400000,
            "ended_reason": "user_exit",
            "start_date": "2026-02-09",
            "start_weather_time_local": "Fog",
            "session_traffic": 0.43,
        },
        {
            "session_id": "sess_009",
            "user_id": "USER_002",
            "study_space_id": 34682,
            "building_id": "ALP",
            "started_at": "2026-02-09 15:10:00",
            "ended_at": None,
            "duration_ms": None,
            "ended_reason": None,
            "start_date": "2026-02-09",
            "start_weather_time_local": "Cloudy",
            "session_traffic": 0.70,
        },
    ]

    bookmarks = [
        {
            "user_id": "USER_001",
            "study_space_id": 44704,
            "building_id": "GSC",
            "created_at": "2026-02-01 10:00:00",
            "deleted_at": None,
        },
        {
            "user_id": "USER_002",
            "study_space_id": 155343,
            "building_id": "LLIB",
            "created_at": "2026-02-02 16:45:00",
            "deleted_at": None,
        },
        {
            "user_id": "USER_001",
            "study_space_id": 44708,
            "building_id": "GSC",
            "created_at": "2026-02-11 09:45:00",
            "deleted_at": None,
        },
    ]

    spot_feedback = [
        {
            "user_id": "USER_001",
            "study_space_id": 44672,
            "building_id": "SLIB",
            "rating": "4",
            "updated_at": "2026-02-05 20:10:00",
        },
        {
            "user_id": "USER_002",
            "study_space_id": 34681,
            "building_id": "ALP",
            "rating": "5",
            "updated_at": "2026-02-06 20:20:00",
        },
        {
            "user_id": "USER_001",
            "study_space_id": 44668,
            "building_id": "SLIB",
            "rating": "4",
            "updated_at": "2026-02-08 14:10:00",
        },
        {
            "user_id": "USER_002",
            "study_space_id": 44706,
            "building_id": "GSC",
            "rating": "1",
            "updated_at": "2026-02-08 18:15:00",
        },
        {
            "user_id": "USER_001",
            "study_space_id": 155343,
            "building_id": "LLIB",
            "rating": "3",
            "updated_at": "2026-02-09 11:05:00",
        },
        {
            "user_id": "USER_001",
            "study_space_id": 168435,
            "building_id": "LLIB",
            "rating": "1",
            "updated_at": "2026-02-14 09:05:00",
        },
    ]

    spot_detail_views = [
        {
            "user_id": "USER_001",
            "study_space_id": 44672,
            "building_id": "SLIB",
            "opened_at": "2026-02-05 18:20:00",
            "closed_at": "2026-02-05 18:21:30",
            "dwell_ms": 90000,
            "source": "recommendation",
            "list_rank": 1,
        },
        {
            "user_id": "USER_002",
            "study_space_id": 34681,
            "building_id": "ALP",
            "opened_at": "2026-02-05 18:50:00",
            "closed_at": "2026-02-05 18:50:20",
            "dwell_ms": 20000,
            "source": "search",
            "list_rank": 4,
        },
        {
            "user_id": "USER_001",
            "study_space_id": 44704,
            "building_id": "GSC",
            "opened_at": "2026-02-07 14:10:00",
            "closed_at": "2026-02-07 14:12:30",
            "dwell_ms": 150000,
            "source": "recommendation",
            "list_rank": 1,
        },
        {
            "user_id": "USER_002",
            "study_space_id": 34681,
            "building_id": "ALP",
            "opened_at": "2026-02-07 18:30:00",
            "closed_at": "2026-02-07 18:30:25",
            "dwell_ms": 25000,
            "source": "search",
            "list_rank": 3,
        },
        {
            "user_id": "USER_001",
            "study_space_id": 44668,
            "building_id": "SLIB",
            "opened_at": "2026-02-08 13:05:00",
            "closed_at": "2026-02-08 13:07:40",
            "dwell_ms": 155000,
            "source": "recommendation",
            "list_rank": 2,
        },
        {
            "user_id": "USER_002",
            "study_space_id": 44706,
            "building_id": "GSC",
            "opened_at": "2026-02-08 17:45:00",
            "closed_at": "2026-02-08 17:45:18",
            "dwell_ms": 18000,
            "source": "search",
            "list_rank": 6,
        },
        {
            "user_id": "USER_001",
            "study_space_id": 155343,
            "building_id": "LLIB",
            "opened_at": "2026-02-09 09:10:00",
            "closed_at": "2026-02-09 09:13:20",
            "dwell_ms": 190000,
            "source": "bookmark",
            "list_rank": None,
        },
        {
            "user_id": "USER_002",
            "study_space_id": 34682,
            "building_id": "ALP",
            "opened_at": "2026-02-09 14:55:00",
            "closed_at": "2026-02-09 14:55:08",
            "dwell_ms": 8000,
            "source": "recommendation",
            "list_rank": 1,
        },
    ]

    search_filters =  [
    {
        "user_id": "USER_001",
        "min_capacity": 1,
        "max_capacity": 4,
        "tech_enhanced": 1,
        "has_printer": 1,
        "is_indoor": 1,
        "is_talking_allowed": 0
    },
    {
        "user_id": "USER_001",
        "min_capacity": 2,
        "max_capacity": 6,
        "tech_enhanced": 0,
        "has_printer": 1,
        "is_indoor": 1,
        "is_talking_allowed": 1
    },
    {
        "user_id": "USER_001",
        "min_capacity": 1,
        "max_capacity": 2,
        "tech_enhanced": 0,
        "has_printer": 0,
        "is_indoor": 1,
        "is_talking_allowed": 0
    },

    # USER 2 — three searches
    {
        "user_id": "USER_002",
        "min_capacity": 3,
        "max_capacity": 8,
        "tech_enhanced": 1,
        "has_printer": 0,
        "is_indoor": 1,
        "is_talking_allowed": 1
    },
    {
        "user_id": "USER_002",
        "min_capacity": 2,
        "max_capacity": 5,
        "tech_enhanced": 1,
        "has_printer": 1,
        "is_indoor": 0,
        "is_talking_allowed": 0
    },
    {
        "user_id": "USER_002",
        "min_capacity": 4,
        "max_capacity": 10,
        "tech_enhanced": 0,
        "has_printer": 1,
        "is_indoor": 1,
        "is_talking_allowed": 1
    }
]
    def insert_dicts(table, rows):
        if not rows:
            return
        cols = rows[0].keys()
        col_sql = ", ".join(cols)
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"INSERT OR REPLACE INTO {table} ({col_sql}) VALUES ({placeholders})"
        values = [tuple(r[c] for c in cols) for r in rows]
        user_cur.executemany(sql, values)

    insert_dicts("users", users)
    insert_dicts("study_sessions", study_sessions)
    insert_dicts("bookmarks", bookmarks)
    insert_dicts("spot_feedback", spot_feedback)
    insert_dicts("spot_detail_views", spot_detail_views)
    insert_dicts("search_filters ", search_filters)

    user_conn.commit()
    user_conn.close()

    print("Fake user data inserted into user_data.db")


if __name__ == "__main__":

    conn = sqlite3.connect(USER_DB)
    cur = conn.cursor()

    #read schema SQL
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    
    # execute schema
    clear_spot_feedback(cur)
    cur.executescript(schema_sql)
    conn.commit()
    conn.close()

    main()