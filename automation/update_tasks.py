from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"

from utils.library_traffic import LibraryTraffic
from utils.weather_api import WeatherAPI

"""
set the class up
"""
library_traffic = LibraryTraffic("https://anteaterapi.com/v2/rest/libraryTraffic", [{"libraryName": "Langson Library"}, {"libraryName": "Science Library"}, {"libraryName": "Gateway Study Center"}], DB_PATH)
weather_api = WeatherAPI()
    
def update_data():
    """
    Replace this with existing update function call(s).
    Example:
    """
    library_traffic.update_database()
    weather_api.update_weather_database()
    pass
