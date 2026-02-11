import sys
from pathlib import Path
import sqlite3
import json
import math
from datetime import datetime
from dateutil import parser  

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from utils.query import DB_PATH, PERSONAL_MODEL_DB_PATH
from utils.query import retrieve_ranked_study_spaces, display_ranked_results

def get_user_1_ranked_results(debug=True):
    filters = {
        "capacity_range": "1-4",
        "indoor": True
    }
    ranked_spaces_result = retrieve_ranked_study_spaces(
                        user_id="USER_001",
                        filters=filters,
                        debug=debug
                    )
    display_ranked_results(ranked_spaces_result)

def get_user_2_ranked_results(debug=True):
    filters = {
        "capacity_range": "1-4",
        "indoor": True
    }
    ranked_spaces_result = retrieve_ranked_study_spaces(
                        user_id="USER_002",
                        filters=filters,
                        debug=debug
                    )
    display_ranked_results(ranked_spaces_result)

def run():
    print("\n\n===== RANKED RESULTS FOR USER 1 =====")
    get_user_1_ranked_results(debug=True)

    print("\n\n===== RANKED RESULTS FOR USER 2 =====")
    get_user_2_ranked_results(debug=True)


if __name__ == "__main__":
    run()
