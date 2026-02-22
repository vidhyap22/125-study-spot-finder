from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.floor_info import correspondence

BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
SCHEMA_PATH = BASE_DIR / "data" / "database" / "user_data_schema.sql"
APP_DB = BASE_DIR / "data" / "database" / "app.db"

TRAFFIC_TABLE = "library_traffic"

def round_to_nearest_hour(date_str: str, time_str: str):
    """
    date_str: 'YYYY-MM-DD'
    time_str: 'HH:MM' or 'HH:MM:SS'
    Returns: (rounded_date_str, rounded_hour_str) where hour_str is 'HH:MM'
    """
    try:
        hour, minute = map(int, time_str.split(":"))
    except ValueError:
        raise ValueError("time_str must be in format 'HH:MM'")

    base_date = datetime.strptime(date_str, "%Y-%m-%d")
    dt = base_date.replace(hour=hour, minute=minute)

    rounded = (dt + timedelta(minutes=30)).replace(
        minute=0,
        second=0,
        microsecond=0
    )

    return rounded.strftime("%Y-%m-%d"), rounded.strftime("%H:%M")


def get_closest_time_weather(date, start_time):
    d, t = round_to_nearest_hour(date, start_time)
    query = """
        SELECT *
        FROM hourly_weather
        WHERE date = ? AND hour = ?
        LIMIT 1;
    """

    with sqlite3.connect(APP_DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(query, (d, t)).fetchone()
    return dict(row)["weather_text"] if row else None

def avg_traffic_between(building_id: str, location_name: str, start_date: str, start_hour: str, end_date: str, end_hour: str):
    """
    start_date/end_date: 'YYYY-MM-DD'
    start_hour/end_hour: 'HH:MM' (already rounded if you want)
    Assumes DB timestamp is ISO UTC like '2026-02-08T00:00:45.980Z'.
    """

    # Build ISO timestamps for filtering (Z = UTC)
    start_dt = datetime.strptime(f"{start_date} {start_hour}", "%Y-%m-%d %H:%M")
    end_dt   = datetime.strptime(f"{end_date} {end_hour}", "%Y-%m-%d %H:%M")
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso   = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    sql = f"""
    WITH hourly AS (
        SELECT
            strftime('%Y-%m-%dT%H:00:00Z', timestamp) AS hour_bucket,
            AVG(traffic_percentage) AS hour_avg
        FROM {TRAFFIC_TABLE}
        WHERE building_id = ?
        AND location_name = ?
        AND timestamp >= ?
        AND timestamp < ?
        GROUP BY hour_bucket
    )
    SELECT
        AVG(hour_avg) AS avg_traffic,
        COUNT(*) AS hours_counted
    FROM hourly;
    """

    with sqlite3.connect(APP_DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(sql, (building_id, location_name, start_iso, end_iso)).fetchone()

    # If no data at all in that interval
    if row is None or row["hours_counted"] == 0:
        return {"avg_traffic": None, "hours_counted": 0}

    return {"avg_traffic": float(row["avg_traffic"]), "hours_counted": int(row["hours_counted"])}

def non_library_traffic(start_date, start_time, end_date, end_time):
    estimated_traffic = {"morning": 0.3, "afternoon": 0.6, "evening": 0.4, "night": 0.2}

    start_date, start_hour = round_to_nearest_hour(start_date, start_time)
    end_date, end_hour = round_to_nearest_hour(end_date, end_time)

    start_dt = datetime.strptime(f"{start_date} {start_hour}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{end_date} {end_hour}", "%Y-%m-%d %H:%M")


    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    current = start_dt
    traffic_values = []

    while current < end_dt:
        hour = current.hour

        if 8 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 22:
            period = "evening"
        else:
            period = "night"

        traffic_values.append(estimated_traffic[period])

        current += timedelta(hours=1)

    if not traffic_values:
        return 0

    return sum(traffic_values) / len(traffic_values)

def get_library_traffic(building, spot_id, start_time, end_time, start_date, end_date):
    libraries = ["LLIB", "SLIB", "GSC", "MLTM"]
  

    if building not in libraries:
        return non_library_traffic(start_date, start_time, end_date, end_time)
             
    else:
        pair = correspondence.get(spot_id)
        if not pair:
            return non_library_traffic(start_date, start_time, end_date, end_time)
        building_id, location_name = pair

        rounded_start_date, start_hour = round_to_nearest_hour(start_date, start_time)
        rounded_end_date, end_hour = round_to_nearest_hour(end_date, end_time)

        result = avg_traffic_between(building_id, location_name, rounded_start_date, start_hour, rounded_end_date, end_hour)

        if result["avg_traffic"] is None:
            return non_library_traffic(start_date, start_time, end_date, end_time)
        else:
            return result["avg_traffic"]
