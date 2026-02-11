"""
query.py - Search the inverted index and answer user queries
"""

import sqlite3
import json
import math
from pathlib import Path
from datetime import datetime
from dateutil import parser  

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"
PERSONAL_MODEL_DB_PATH = BASE_DIR / "data" / "database" / "user_data.db"
INDEX_PATH = BASE_DIR / "data" / "filters_index.json"


def load_index():
    """Load the pre-built filter index"""
    with open(INDEX_PATH, 'r') as f:
        return json.load(f)


def search_with_filters(filters):
    """
    Based on the filters the user has specified, extract the study rooms matching each filter from the inverted index. Then, intersect to get only the study room ids that match all the filters.

    Args:
        filters (dict): Filter criteria
            {
                "capacity_range": "5-10",
                "talking_allowed": True,
                "study_room": False,
                "indoor": True,
                "tech_enhanced": True,
                "has_printer": True,
                "building": "LANGSON"
            }
    
    Returns:
        list: List of matching study_space_ids
    """
    indexes = load_index()
    
    # Start with all possible study spaces
    result_sets = []
    
    # Apply each filter
    if "capacity_range" in filters and filters["capacity_range"]:
        key = str(filters["capacity_range"])
        if key in indexes["capacity_ranges"]:
            result_sets.append(set(indexes["capacity_ranges"][key]))
        else:
            return []  # Invalid capacity range
    
    if "talking_allowed" in filters and filters["talking_allowed"] is not None:
        key = str(filters["talking_allowed"]).lower()
        if key in indexes["talking_allowed"]:
            result_sets.append(set(indexes["talking_allowed"][key]))
    
    if "study_room" in filters and filters["study_room"] is not None:
        key = str(filters["study_room"]).lower()
        if key in indexes["study_room"]:
            result_sets.append(set(indexes["study_room"][key]))
    
    if "indoor" in filters and filters["indoor"] is not None:
        key = str(filters["indoor"]).lower()
        if key in indexes["indoor"]:
            result_sets.append(set(indexes["indoor"][key]))
    
    if "tech_enhanced" in filters and filters["tech_enhanced"] is not None:
        key = str(filters["tech_enhanced"]).lower()
        if key in indexes["tech_enhanced"]:
            result_sets.append(set(indexes["tech_enhanced"][key]))
    
    if "has_printer" in filters and filters["has_printer"] is not None:
        key = str(filters["has_printer"]).lower()
        if key in indexes["has_printer"]:
            result_sets.append(set(indexes["has_printer"][key]))
    
    if "building" in filters and filters["building"]:
        key = filters["building"].upper()
        if key in indexes["building"]:
            result_sets.append(set(indexes["building"][key]))
        else:
            return []  # Invalid building
    
    # Intersect all sets to find spaces matching ALL filters
    if not result_sets:
        return []
    
    matching_spaces = result_sets[0]
    for result_set in result_sets[1:]:
        matching_spaces = matching_spaces.intersection(result_set)
    
    return list(matching_spaces)


def check_current_availability_window(db_conn, space_ids, start_time=None, end_time=None):
    """
    If a space requires reservation, check if it is currently available. We are only focused on corrently avaiable rooms since users are most likely looking for a place to study immediately. In the future, we can expand to allow users to search for rooms available during a specific time window.

    Logic:
    - If must_reserve = 0 → always available
    - If must_reserve = 1 → must have availability window

    Return study_space_ids that are currently available.
    """

    if not space_ids:
        return []

    cursor = db_conn.cursor()

    placeholders = ",".join("?" * len(space_ids))

    # Case 1: Check availability for a specific time window (not currently used)
    if start_time and end_time:
        query = f"""
        SELECT DISTINCT s.study_space_id
        FROM study_spaces s
        LEFT JOIN room_availability ra
            ON s.study_space_id = ra.study_space_id
        WHERE s.study_space_id IN ({placeholders})
        AND (
            s.must_reserve = 0
            OR (
                s.must_reserve = 1
                AND ra.is_available = 1
                AND ra.start_time <= ?
                AND ra.end_time >= ?
                AND datetime(ra.scraped_at) > datetime('now','-24 hours')
            )
        )
        """

        params = space_ids + [start_time, end_time]

    # Case #2: Check availability for the current time (default)
    else:

        query = f"""
        SELECT DISTINCT s.study_space_id
        FROM study_spaces s
        LEFT JOIN room_availability ra
            ON s.study_space_id = ra.study_space_id
        WHERE s.study_space_id IN ({placeholders})
        AND (
            s.must_reserve = 0
            OR (
                s.must_reserve = 1
                AND ra.is_available = 1
                AND datetime('now') BETWEEN ra.start_time AND ra.end_time
                AND datetime(ra.scraped_at) > datetime('now','-24 hours')
            )
        )
        """

        params = space_ids

    cursor.execute(query, params)

    available_ids = [row[0] for row in cursor.fetchall()]

    return available_ids

def load_personal_model_signals(personal_model_db_conn, user_id, available_study_ids):
    """
    Load personal model signals ONLY for currently available study spaces.

    Args:
        conn: sqlite3 connection
        user_id (str): user identifier
        available_study_ids (list[int]): study spaces currently eligible

    Returns:
        dict:
        {
            "dwell_map": {study_space_id: total_dwell_ms},
            "study_session_map": {study_space_id: [(duration_ms, ended_reason)]}
        }
    """

    cursor = personal_model_db_conn.cursor()

    if not available_study_ids:
        return {
            "dwell_map": {},
            "study_session_map": {}
        }

    placeholders = ",".join(["?"] * len(available_study_ids))

    # User spent some time looking at certain study spaces.
    cursor.execute(f"""
        SELECT study_space_id, SUM(COALESCE(dwell_ms,0))
        FROM spot_detail_views
        WHERE user_id = ?
        AND study_space_id IN ({placeholders})
        GROUP BY study_space_id
    """, (user_id, *available_study_ids))

    dwell_map = {row[0]: row[1] for row in cursor.fetchall()}

    # User previously studied in some study spaces.
    cursor.execute(f"""
        SELECT study_space_id, duration_ms, ended_reason
        FROM study_sessions
        WHERE user_id = ?
        AND study_space_id IN ({placeholders})
    """, (user_id, *available_study_ids))

    study_session_map = {}

    for study_space_id, duration, reason in cursor.fetchall():
        if study_space_id not in study_session_map:
            study_session_map[study_space_id] = []
        study_session_map[study_space_id].append((duration, reason))

    return {
        "dwell_map": dwell_map,
        "study_session_map": study_session_map
    }

def get_space_details(db_conn, space_ids):
    """
    Fetch full details for matching spaces
    
    Args:
        space_ids (list): List of study_space_ids
    
    Returns:
        list: List of dicts with space details
    """
    if not space_ids:
        return []
    
    cursor = db_conn.cursor()
    
    placeholders = ','.join('?' * len(space_ids))
    cursor.execute(f"""
        SELECT 
            s.study_space_id,
            s.name,
            s.capacity,
            s.is_talking_allowed,
            s.must_reserve,
            s.is_indoor,
            s.tech_enhanced,
            s.building_id,
            b.name as building_name,
            b.has_printer,
            b.latitude,
            b.longitude
        FROM study_spaces s
        LEFT JOIN buildings b ON s.building_id = b.building_id
        WHERE s.study_space_id IN ({placeholders})
    """, space_ids)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row[0],
            "name": row[1],
            "capacity": row[2],
            "talking_allowed": bool(row[3]),
            "must_reserve": bool(row[4]),
            "indoor": bool(row[5]),
            "tech_enhanced": bool(row[6]),
            "building_id": row[7],
            "building_name": row[8],
            "has_printer": bool(row[9]) if row[9] is not None else None,
            "latitude": row[10],
            "longitude": row[11]
        })
    
    return results

def rank_spaces_with_personal_model(space_details, personal_signals, filters=None):
    """
    Rank study spaces by combining filter-based scoring with personal model signals. The personal model signals include:
        - Dwell time: Total time spent viewing the study space details in the app. 
        - Study sessions: Past study sessions booked in that space, including duration and how the session ended (e.g., user exit, noise, etc.).
    """

    dwell_map = personal_signals.get("dwell_map", {})
    study_session_map = personal_signals.get("study_session_map", {})

    ranked = []

    for space in space_details:
        study_space_id = space["id"]
        score = 0

        # --- BASELINE RANKING ---
        # Rank based on filters that user has specified. This ensures that spaces that better match the user's stated preferences are ranked higher.
        if filters:

            if filters.get("tech_enhanced") and space.get("tech_enhanced"):
                score += 3

            if filters.get("indoor") and space.get("indoor"):
                score += 2

            if filters.get("talking_allowed") == space.get("talking_allowed"):
                score += 2

            if filters.get("has_printer") and space.get("has_printer"):
                score += 2

            if filters.get("capacity_range") and space.get("capacity"):
                try:
                    low, high = map(int, filters["capacity_range"].split("-"))
                    if low <= space["capacity"] <= high:
                        score += 3
                except:
                    pass

        if not space.get("must_reserve"):
            score += 1

        # --- PERSONAL MODEL ---
        # Take dwell time into account when user showed interest in the study space details. This can indicate a stronger preference for that space.
        dwell = dwell_map.get(study_space_id, 0)
        if dwell > 0:
            score += min(5, dwell / 60000)  # ~1 point per minute

        # Take past study sessions users have booked in that space into account. Longer sessions and sessions that ended positively (e.g., user exit) can indicate a stronger preference for that space, while sessions that ended due to noise can indicate a negative experience.
        if study_space_id in study_session_map:
            for duration, reason in study_session_map[study_space_id]:

                if duration:
                    score += min(6, duration / (30 * 60 * 1000))

                if reason == "user_exit":
                    score += 4
                elif reason == "noise":
                    score -= 3

        space["score"] = round(score, 2)
        ranked.append(space)

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked

def display_ranked_results(ranked_spaces, top_n=10):
    """
    Display ranked results in a user-friendly format
    """
    print(f"\nTop {top_n} Ranked Study Spaces:")
    for space in ranked_spaces[:top_n]:
        print(f"{space['name']} (Score: {space['score']}) - {space['building_name']} - Capacity: {space['capacity']} - {'Indoor' if space['indoor'] else 'Outdoor'} - {'Tech-Enhanced' if space['tech_enhanced'] else 'Standard'} - {'Talking Allowed' if space['talking_allowed'] else 'Quiet Only'} - {'Must Reserve' if space['must_reserve'] else 'No Reservation Needed'}")

def retrieve_ranked_study_spaces(user_id, filters, debug=False):
    db_conn = sqlite3.connect(DB_PATH)
    personal_model_db_conn = sqlite3.connect(PERSONAL_MODEL_DB_PATH)

    # Step 1: Search by the filters the user inputs into the frontend.
    matching_ids = search_with_filters(filters)
    if debug:
        print("\nMatching study_room_IDs after filters:")
        print(matching_ids)
        print("Total:", len(matching_ids))
    
    if not matching_ids:
        return []

    # Step 2: Check room availability for the matching IDs. This will filter out any rooms that require reservation but are not currently available.
    available_ids = check_current_availability_window(db_conn, matching_ids)
    if debug:
        print("\nAvailable study_room_IDs RIGHT NOW:")
        print(available_ids)
        print("Total:", len(available_ids))

    if not available_ids:
        return []

    # Step 3: Load personal model signals for the currently available study spaces.
    user_personal_model_signals = load_personal_model_signals(personal_model_db_conn, user_id, available_ids)
    if debug:
        print(f"\nPersonal model signals for User (user_id={user_id}):")
        print(user_personal_model_signals)
    
    # Step 4: Fetch full details for the currently available study spaces.
    space_details = get_space_details(db_conn, available_ids)

    # Step 5: Rank spaces by combining filter-based scoring with personal model signals.
    ranked_spaces = rank_spaces_with_personal_model(space_details, user_personal_model_signals, filters)

    return ranked_spaces

def get_available_buildings():
    """Get list of all available buildings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT building_id, name FROM buildings ORDER BY name")
    buildings = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return buildings