import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
APP_DB = BASE_DIR / "data" / "database" / "app.db"
SCHEMA_PATH = BASE_DIR / "data" / "database" / "user_data_schema.sql"
FAKE_DATA_PATH = BASE_DIR / "personal_model" / "fake_user_data.json"


def insert_dicts(table, rows, user_cur):
    if not rows:
        return
    cols = rows[0].keys()
    col_sql = ", ".join(cols)
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"INSERT OR REPLACE INTO {table} ({col_sql}) VALUES ({placeholders})"
    values = [tuple(r[c] for c in cols) for r in rows]
    user_cur.executemany(sql, values)

def main():
    with open(FAKE_DATA_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)

    study_sessions = payload.get("study_sessions", [])
    bookmarks = payload.get("bookmarks", [])
    spot_feedback = payload.get("spot_feedback", [])
    search_filters = payload.get("search_filters", [])
 
    user_conn = sqlite3.connect(USER_DB)
    user_cur = user_conn.cursor()
    users = [
        {
            "user_id": "USER_003",
            "created_at": "2026-01-10 09:00:00",
        },
        {
            "user_id": "USER_004",
            "created_at": "2026-01-15 14:30:00",
        },
        {
            "user_id": "USER_004",
            "created_at": "2026-01-15 14:30:00",
        }
    ]
    
    #user_cur.execute("""
    #DELETE FROM study_sessions
    #WHERE user_id IN ('USER_004','USER_005','USER_006')
    #""")

    #user_cur.execute("""
    #DELETE FROM sqlite_sequence
    #WHERE name='study_sessions'
    #""")

    insert_dicts("users", users, user_cur)
    insert_dicts("study_sessions", study_sessions, user_cur)
    insert_dicts("bookmarks", bookmarks, user_cur)
    insert_dicts("spot_feedback", spot_feedback, user_cur)
    insert_dicts("search_filters ", search_filters, user_cur)

    user_conn.commit()
    user_conn.close()

    print("Fake user data inserted into user_data.db")


if __name__ == '__main__':
    main()