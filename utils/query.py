"""
query.py - Search the inverted index and answer user queries
"""

import sqlite3
import json
import math
from pathlib import Path
from datetime import datetime
from dateutil import parser  
from personal_model.personal_model_process import PersonalModel

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
            }
    
    Returns:
        list: List of matching study_space_ids
    """
    indexes = load_index()
    result_sets = []

    if "capacity_range" in filters and filters["capacity_range"]:
        key = str(filters["capacity_range"])
        if key in indexes["capacity_ranges"]:
            result_sets.append(set(indexes["capacity_ranges"][key]))
        else:
            return []

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

def get_space_details(db_conn, space_ids, filters=None):
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

    query = f"""
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
    """

    params = space_ids

    if filters and "building" in filters and filters["building"]:
        query += " AND UPPER(b.name) = ?"
        params = space_ids + [filters["building"].upper()]

    cursor.execute(query, params)

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


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # distance in km


def compute_final_score(space, probability_map, user_location=None, 
                        prob_weight=0.8, distance_weight=0.2, 
                        distance_decay_km=2):
    """
    Compute final ranking score for a study space.

    Args:
        space (dict): Study space details
        probability_map (dict): {space_id: probability_score}
        user_location (dict): {"lat": float, "lon": float}
        prob_weight (float): Weight for personalization score
        distance_weight (float): Weight for distance boost
        distance_decay_km (float): Distance window for normalization

    Returns:
        float: Final weighted score
    """

    spot_id = space["id"]
    base_score = probability_map.get(spot_id, 0.0)

    distance_score = 0.0
    if (user_location and space.get("latitude") is not None and space.get("longitude") is not None):
        distance_km = calculate_distance(user_location["latitude"], user_location["longitude"], space["latitude"], space["longitude"])

        distance_score = max(0, 1 - (distance_km / distance_decay_km))

    final_score = (prob_weight * base_score) + (distance_weight * distance_score)

    return round(final_score, 4)


def display_ranked_results(ranked_spaces, top_n=10):
    """
    Display ranked results in a user-friendly format
    """
    if not ranked_spaces:
        return 
    
    print(f"\nTop {top_n} Ranked Study Spaces:")
    for space in ranked_spaces[:top_n]:
        print(f"{space['name']} (Score: {space['score']}) - {space['building_name']} - Capacity: {space['capacity']} - {'Indoor' if space['indoor'] else 'Outdoor'} - {'Tech-Enhanced' if space['tech_enhanced'] else 'Standard'} - {'Talking Allowed' if space['talking_allowed'] else 'Quiet Only'} - {'Must Reserve' if space['must_reserve'] else 'No Reservation Needed'}")


def retrieve_ranked_study_spaces(user_id, filters, user_location=None, debug=False):
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
        if debug:
            print("No study spaces are currently available based on the filters and availability.")
        return 
    
    # Step 3: Fetch full details for the currently available study spaces.
    space_details = get_space_details(db_conn, available_ids)

    # Step 4: Use personal model signals from the probability model to adjust the ranking of the study spaces. This allows us to personalize the results based on the user's past interactions and preferences.
    personal_model = PersonalModel(user_id, USER_DB=PERSONAL_MODEL_DB_PATH, APP_DB=DB_PATH)
    personal_model.user_context_for_ranking()
    probability_results = personal_model.probability(available_ids)
    if debug:
        print(f"\nPersonal model probabilities for User (user_id={user_id}):")
        print(probability_results)
    probability_map = {spot_id: score for spot_id, score in probability_results}

    # Step 5: Attach score after weighting personal model signals to each study space and take proximity of study space into account.
    for space in space_details:
        space["score"] = compute_final_score(space, probability_map, user_location)
    
    # Step 6: Sort the study spaces by the combined score (filter-based + personal model) to get a personalized ranking of study spaces for the user.
    ranked_spaces = sorted(space_details, key=lambda x: x["score"], reverse=True)

    return ranked_spaces


def get_available_buildings():
    """Get list of all available buildings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT building_id, name FROM buildings ORDER BY name")
    buildings = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return buildings