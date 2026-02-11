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

def get_user_1_results_for_capacity_1to4_and_indoor_filter(debug=True):
    filters = {
        "capacity_range": "1-4",
        "indoor": True
    }
    ranked_spaces_result = retrieve_ranked_study_spaces(
                        user_id="USER_001",
                        filters=filters,
                        debug=debug
                    )
    print_filters_and_ranked_results(filters, ranked_spaces_result)

def get_user_2_results_for_capacity_1to4_and_indoor_filter(debug=True):
    filters = {
        "capacity_range": "1-4",
        "indoor": True
    }
    ranked_spaces_result = retrieve_ranked_study_spaces(
                        user_id="USER_002",
                        filters=filters,
                        debug=debug
                    )
    print_filters_and_ranked_results(filters, ranked_spaces_result)

def get_user_1_results_for_indoor_and_techenhanced_filter(debug=True):
    filters = {
        "indoor": True,
        "tech_enhanced": True
    }
    ranked_spaces_result = retrieve_ranked_study_spaces(
                        user_id="USER_001",
                        filters=filters,
                        debug=debug
                    )
    print_filters_and_ranked_results(filters, ranked_spaces_result)


def print_filters_and_ranked_results(filters, ranked_spaces_result):
    print("\nApplied Filters:")
    for key, value in filters.items():
        print(f"  {key}: {value}")
    display_ranked_results(ranked_spaces_result)

def run():
    print("\n\n===== RANKED RESULTS FOR USER 1 =====")
    get_user_1_results_for_capacity_1to4_and_indoor_filter(debug=True)

    print("\n\n===== RANKED RESULTS FOR USER 2 =====")
    get_user_2_results_for_capacity_1to4_and_indoor_filter(debug=True)

    print("\n\n===== RANKED RESULTS FOR USER 1 =====")
    get_user_1_results_for_indoor_and_techenhanced_filter(debug=True)


if __name__ == "__main__":
    run()
