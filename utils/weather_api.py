from pathlib import Path
import sqlite3
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
current_params = {
	"latitude": 33.64697986198167, 
	"longitude": -117.84219777551814,
    "current": "temperature_2m,precipitation,weathercode,wind_speed_10m,rain",
    "timezone": "America/Los_Angeles"
}

hourly_params = {
    "latitude": 33.64697986198167, 
	"longitude": -117.84219777551814,
    "hourly": "temperature_2m,precipitation,weathercode,wind_speed_10m,rain",
    "timezone": "America/Los_Angeles"
}

def create_hourly_weather_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hourly_weather (
        time_local TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        hour TEXT NOT NULL,
        temperature_c REAL,
        precip_mm REAL,
        is_raining INTEGER NOT NULL,
        weather_code INTEGER,
        weather_text TEXT,
        fetched_at TEXT NOT NULL
    );
    """)

    
def transform_weather(code):
    if code == 0:
        return "Clear"
    if code in (1, 2):
        return "Partly Cloudy"
    if code == 3:
        return "Cloudy"
    if code in (45, 48):
        return "Fog"
    if 51 <= code <= 57:
        return "Drizzle"
    if 61 <= code <= 67 or 80 <= code <= 82:
        return "Rain"
    if 71 <= code <= 77:
        return "Snow"
    if code == 95:
        return "Thunderstorm"
    return "Other" 

def fetch_current_weather(url, params=current_params):
    """get the current weather"""
    responses = openmeteo.weather_api(url, params=params)
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    current = response.Current()

    return current

def fetch_hourly_weather(url, params=hourly_params):
    """get hourly forecast weather"""
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    return hourly

def store_hourly_weather(cur):

    hourly = fetch_hourly_weather(url)
    if hourly is None:
        raise RuntimeError("Hourly data is None. Check params['hourly'] must be a list.")

    #get the temperature, precipitation, weather code
    temps = hourly.Variables(0).ValuesAsNumpy()
    precip = hourly.Variables(1).ValuesAsNumpy()
    codes = hourly.Variables(2).ValuesAsNumpy().astype(int)

    start = hourly.Time()        
    step = hourly.Interval()    

    fetched_at = requests_cache.datetime.now(requests_cache.timezone.utc).isoformat()

    rows = []
    for i in range(len(temps)):
        t_utc = requests_cache.datetime.fromtimestamp(start + i * step, tz=requests_cache.timezone.utc)
        time_local = t_utc.isoformat()  

        date = time_local[:10]          
        hour = time_local[11:16]        

        is_raining = 1 if float(precip[i]) > 0.0 else 0
        code = int(codes[i])
        #get the weather by code
        text = transform_weather(code)

        rows.append((
            time_local,              
            date,
            hour,
            float(temps[i]),
            float(precip[i]),
            is_raining,
            code,
            text,
            fetched_at
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO hourly_weather
        (time_local, date, hour, temperature_c, precip_mm, is_raining, weather_code, weather_text, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    store_hourly_weather(cur)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()