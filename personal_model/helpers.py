from datetime import datetime, timedelta
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
SCHEMA_PATH = BASE_DIR / "data" / "database" / "user_data_schema.sql"
APP_DB = BASE_DIR / "data" / "database" / "app.db"

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

def get_library_traffic(building, spot_id):
    pass