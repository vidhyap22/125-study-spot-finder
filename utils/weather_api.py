from pathlib import Path
import sqlite3
import openmeteo_requests

import pandas as pd
import requests_cache
import requests
from retry_requests import retry

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"

# Setup the Open-Meteo API client with cache and retry on error
#cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

class WeatherAPI():
    def __init__(self, DB_PATH=DB_PATH):
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.current_params = {
            "latitude": 33.64697986198167, 
            "longitude": -117.84219777551814,
            "current": "temperature_2m,precipitation,weathercode,wind_speed_10m,rain",
            "timezone": "America/Los_Angeles"
        }
        self.hourly_params = {
            "latitude": 33.64697986198167, 
            "longitude": -117.84219777551814,
            "hourly": "temperature_2m,precipitation,weathercode,wind_speed_10m,rain",
            "timezone": "America/Los_Angeles"
        }
        self.retry_session = retry(requests.Session(), retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = self.retry_session)
        self.DB_PATH = DB_PATH

    def create_hourly_weather_table(self):
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()
        cur.execute("""
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
        conn.commit()
        conn.close()

    def clear_weather_database(self, cursor):
        cursor.execute("DELETE FROM library_traffic;")

    def transform_weather(self,code):
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

    def fetch_current_weather(self):
        """get the current weather"""
        responses = self.openmeteo.weather_api(self.url, params=self.current_params)
        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        current = response.Current()

        return current

    def fetch_hourly_weather(self):
        """get hourly forecast weather"""
        responses = self.openmeteo.weather_api(self.url, params=self.hourly_params)
        response = responses[0]
        hourly = response.Hourly()
        return hourly

    def store_hourly_weather(self, cur):
        hourly = self.fetch_hourly_weather()
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
            text = self.transform_weather(code)

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

    def update_weather_database(self):
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()
        self.clear_weather_database(cur)
        self.store_hourly_weather(cur)
        conn.commit()
        conn.close()

    
def main():
    weather_api = WeatherAPI()
    weather_api.update_weather_database()


if __name__ == "__main__":
    main()