import datetime
import sqlite3
from pathlib import Path
import sys
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
APP_DB = BASE_DIR / "data" / "database" / "app.db"

 # helper to load per-user event table from USER_DB
def load_user_table(user_id, table_name: str) -> pd.DataFrame:
    with sqlite3.connect(USER_DB) as conn:
        return pd.read_sql_query(
            f"SELECT * FROM {table_name} WHERE user_id = ?;",
            conn,
            params=(user_id,)
)

def return_enriched_study_session_history(user_id):
    with sqlite3.connect(APP_DB) as conn:
            df_spaces = pd.read_sql_query("SELECT * FROM study_spaces;", conn)
            df_buildings = pd.read_sql_query("SELECT * FROM buildings;", conn)

    df_spaces["study_space_id"] = df_spaces["study_space_id"].astype("int64")
    df_spaces["building_id"] = df_spaces["building_id"].astype("string")
    df_buildings["building_id"] = df_buildings["building_id"].astype("string")

    df_sessions = load_user_table(user_id, "study_sessions")
    return df_sessions


