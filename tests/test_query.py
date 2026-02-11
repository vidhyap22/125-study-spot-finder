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
from utils.query import search_with_filters, check_current_availability_window, load_personal_model_signals, get_space_details, rank_spaces_with_personal_model, display_ranked_results

def get_user_1_ranked_results(debug=True):
    db_conn = sqlite3.connect(DB_PATH)
    personal_model_db_conn = sqlite3.connect(PERSONAL_MODEL_DB_PATH)

    # Search by the filters the user inputs into the frontend.
    filters = {
        "capacity_range": "1-4",
        "indoor": True
    }

    matching_ids = search_with_filters(filters)

    if debug:
        print("\nMatching study_room_IDs after filters:")
        print(matching_ids)
        print("Total:", len(matching_ids))

    # Check room availability for the matching IDs. This will filter out any rooms that require reservation but are not currently available.
    matching_ids = check_current_availability_window(db_conn, matching_ids)
    
    if debug:
        print("\nAvailable study_room_IDs RIGHT NOW:")
        print(matching_ids)
        print("Total:", len(matching_ids))

    user_1_personal_model_signals = load_personal_model_signals(personal_model_db_conn, "USER_001", matching_ids)
    if debug:
        print("\nPersonal model signals for USER_001:")
        print(user_1_personal_model_signals)
    
    space_details = get_space_details(db_conn, matching_ids)
    if debug:
        pass
        #print(space_details)

    ranked1 = rank_spaces_with_personal_model(space_details, user_1_personal_model_signals, filters=filters)    
    
    display_ranked_results(ranked1)

def get_user_2_ranked_results(debug=True):
    db_conn = sqlite3.connect(DB_PATH)
    personal_model_db_conn = sqlite3.connect(PERSONAL_MODEL_DB_PATH)

    # Search by the filters the user inputs into the frontend.
    filters = {
        "capacity_range": "1-4",
        "indoor": True
    }

    matching_ids = search_with_filters(filters)

    if debug:
        print("\nMatching study_room_IDs after filters:")
        print(matching_ids)
        print("Total:", len(matching_ids))

    # Check room availability for the matching IDs. This will filter out any rooms that require reservation but are not currently available.
    matching_ids = check_current_availability_window(db_conn, matching_ids)
    
    if debug:
        print("\nAvailable study_room_IDs RIGHT NOW:")
        print(matching_ids)
        print("Total:", len(matching_ids))

    user_2_personal_model_signals = load_personal_model_signals(personal_model_db_conn, "USER_002", matching_ids)
    if debug:
        print("\nPersonal model signals for USER_001:")
        print(user_2_personal_model_signals)
    
    space_details = get_space_details(db_conn, matching_ids)
    if debug:
        pass
        #print(space_details)

    ranked2 = rank_spaces_with_personal_model(space_details, user_2_personal_model_signals, filters=filters)    
    
    display_ranked_results(ranked2)

def run():
    print("\n\n===== RANKED RESULTS FOR USER 1 =====")
    get_user_1_ranked_results(debug=True)

    print("\n\n===== RANKED RESULTS FOR USER 2 =====")
    get_user_2_ranked_results(debug=True)


if __name__ == "__main__":
    run()
