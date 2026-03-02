"""
query.py - Search the inverted index and answer user queries
"""

import sqlite3
import json
import math
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pytz
import sys
from dateutil import parser  
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
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
    Based on the filters the user has specified, extract the study rooms matching each filter
    from the inverted index. Then, intersect to get only the study room ids that match all filters.

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


def get_next_slot_start_pacific() -> str:
    """
    Returns the next 30-min slot start in Pacific time as an ISO string
    matching the DB format: 2026-03-02T15:30:00-08:00
    """
    pacific = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific)
    
    if now.minute < 30:
        next_slot = now.replace(minute=30, second=0, microsecond=0)
    else:
        next_slot = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    return next_slot.strftime("%Y-%m-%dT%H:%M:%S%z").replace("+0800", "+08:00").replace("-0800", "-08:00")


def get_end_of_day_pacific() -> str:
    """
    Returns 23:30:00 Pacific today — the last valid slot start.
    """
    pacific = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific)
    end_of_day = now.replace(hour=23, minute=30, second=0, microsecond=0)
    return end_of_day.strftime("%Y-%m-%dT%H:%M:%S%z").replace("+0800", "+08:00").replace("-0800", "-08:00")


def check_current_availability_window(db_conn, space_ids, start_time=None, end_time=None):
    """
    Checks availability for spaces that require reservation starting from the next open 30 minute time slot to the end of day (11:30 PM Pacific).
    """
    if not space_ids:
        return []

    cursor = db_conn.cursor()
    placeholders = ",".join("?" * len(space_ids))

    slot_start = start_time if start_time else get_next_slot_start_pacific()
    slot_end = get_end_of_day_pacific()

    # Compare raw strings directly — no datetime() conversion, stays in Pacific
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
            AND ra.start_time >= ?
            AND ra.start_time <= ?
            AND ra.scraped_at > datetime('now', '-24 hours')
        )
    )
    """
    params = space_ids + [slot_start, slot_end]
    cursor.execute(query, params)
    return [row[0] for row in cursor.fetchall()]

def check_next_slot_availability_window(db_conn, space_ids):
    """
    Checks if the immediate next 30-min slot is available.
    e.g. 3:03pm → checks 3:30-4:00pm slot
         2:59pm → checks 3:00-3:30pm slot
         1:00pm → checks 1:30-2:00pm slot
    """
    if not space_ids:
        return []

    pacific = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific)

    # Calculate next slot start
    if now.minute < 30:
        next_slot_start = now.replace(minute=30, second=0, microsecond=0)
    else:
        next_slot_start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    next_slot_end = next_slot_start + timedelta(minutes=30)

    slot_start_str = next_slot_start.strftime("%Y-%m-%dT%H:%M:%S%z").replace("+0800", "+08:00").replace("-0800", "-08:00")
    slot_end_str = next_slot_end.strftime("%Y-%m-%dT%H:%M:%S%z").replace("+0800", "+08:00").replace("-0800", "-08:00")

    cursor = db_conn.cursor()
    placeholders = ",".join("?" * len(space_ids))

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
            AND ra.start_time = ?
            AND ra.end_time = ?
            AND ra.scraped_at > datetime('now', '-24 hours')
        )
    )
    """
    params = space_ids + [slot_start_str, slot_end_str]
    cursor.execute(query, params)
    return [row[0] for row in cursor.fetchall()]


# def check_current_availability_window(db_conn, space_ids, start_time=None, end_time=None):
#     """
#     If a space requires reservation, check if it is currently available.
#     We are only focused on currently available rooms since users are most likely
#     looking for a place to study immediately.

#     Logic:
#     - If must_reserve = 0 → always available
#     - If must_reserve = 1 → must have a valid availability window
#     """
#     if not space_ids:
#         return []

#     cursor = db_conn.cursor()
#     placeholders = ",".join("?" * len(space_ids))

#     if start_time and end_time:
#         query = f"""
#         SELECT DISTINCT s.study_space_id
#         FROM study_spaces s
#         LEFT JOIN room_availability ra
#             ON s.study_space_id = ra.study_space_id
#         WHERE s.study_space_id IN ({placeholders})
#         AND (
#             s.must_reserve = 0
#             OR (
#                 s.must_reserve = 1
#                 AND ra.is_available = 1
#                 AND datetime(?) BETWEEN datetime(ra.start_time) AND datetime(ra.end_time)
#                 AND datetime(ra.scraped_at) > datetime('now', '-24 hours')
#             )
#         )
#         """
#         params = space_ids + [start_time]
#     else:
#         query = f"""
#         SELECT DISTINCT s.study_space_id
#         FROM study_spaces s
#         LEFT JOIN room_availability ra
#             ON s.study_space_id = ra.study_space_id
#         WHERE s.study_space_id IN ({placeholders})
#         AND (
#             s.must_reserve = 0
#             OR (
#                 s.must_reserve = 1
#                 AND ra.is_available = 1
#                 AND datetime('now')
#                     BETWEEN datetime(ra.start_time)
#                     AND datetime(ra.end_time)
#                 AND datetime(ra.scraped_at) > datetime('now', '-24 hours')
#             )
#         )
#         """
#         params = space_ids

#     cursor.execute(query, params)
#     return [row[0] for row in cursor.fetchall()]


def get_space_details(db_conn, space_ids, filters=None):
    """
    Fetch full details for matching spaces.

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
            s.floor,
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
            "floor": row[8],
            "building_name": row[9],
            "has_printer": bool(row[10]) if row[10] is not None else None,
            "latitude": row[11],
            "longitude": row[12]
        })

    return results


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def compute_final_score(space, probability_map, user_location=None,
                        prob_weight=0.8, distance_weight=0.2,
                        distance_decay_km=2):
    """
    Compute final ranking score for a study space.

    Args:
        space (dict): Study space details
        probability_map (dict): {space_id: probability_score}
        user_location (dict): {"latitude": float, "longitude": float}
        prob_weight (float): Weight for personalization score
        distance_weight (float): Weight for distance boost
        distance_decay_km (float): Distance window for normalization

    Returns:
        float: Final weighted score
    """
    spot_id = space["id"]
    base_score = probability_map.get(spot_id, 0.0)

    distance_score = 0.0
    if (user_location and
            space.get("latitude") is not None and
            space.get("longitude") is not None):
        distance_km = calculate_distance(
            user_location["latitude"], user_location["longitude"],
            space["latitude"], space["longitude"]
        )
        distance_score = max(0, 1 - (distance_km / distance_decay_km))

    return round((prob_weight * base_score) + (distance_weight * distance_score), 4)


def display_ranked_results(ranked_spaces, top_n=10):
    """Display ranked results in a user-friendly format"""
    if not ranked_spaces:
        return

    print(f"\nTop {top_n} Ranked Study Spaces:")
    for space in ranked_spaces[:top_n]:
        floor_text = f" - Floor: {space['floor']}" if space.get("floor") not in [None, "N", ""] else ""
        print(
            f"{space['name']} (Score: {space['score']})\n"
            f"  {space['building_name']}{floor_text}\n"
            f"  Capacity: {space['capacity']}\n"
            f"  {'Indoor' if space['indoor'] else 'Outdoor'}\n"
            f"  {'Tech-Enhanced' if space['tech_enhanced'] else 'Standard'}\n"
            f"  {'Talking Allowed' if space['talking_allowed'] else 'Quiet Only'}\n"
            f"  {'Must Reserve' if space['must_reserve'] else 'No Reservation Needed'}\n"
        )


def _build_relax_order(filters, avg_stats):
    """
    Build a list of filter keys sorted by ascending importance (weakest first),
    so we know which constraints to relax first.

    capacity_range is treated as maximally important (1.0) since the user
    explicitly chose a size — it's the last thing we'd want to relax.
    """
    importance_map = {}

    if "indoor" in filters and filters["indoor"] is not None:
        importance_map["indoor"] = avg_stats.get("is_indoor_pct", 0.5)
    if "talking_allowed" in filters and filters["talking_allowed"] is not None:
        importance_map["talking_allowed"] = avg_stats.get("is_talking_allowed_pct", 0.5)
    if "has_printer" in filters and filters["has_printer"] is not None:
        importance_map["has_printer"] = avg_stats.get("has_printer_pct", 0.5)
    if "tech_enhanced" in filters and filters["tech_enhanced"] is not None:
        importance_map["tech_enhanced"] = avg_stats.get("tech_enhanced_pct", 0.5)
    if "capacity_range" in filters and filters["capacity_range"]:
        importance_map["capacity_range"] = 1.0

    return sorted(importance_map.keys(), key=lambda k: importance_map[k])


def progressive_filter_search(db_conn, filters, avg_stats, debug=False):
    """
    Try all user filters as hard constraints first. If the matched rooms have
    at least one currently available room, return those available IDs immediately.

    If nothing is available, relax the lowest-priority constraint and retry.
    Keep relaxing until we find available rooms or run out of constraints.

    Availability is checked at every step so relaxation is driven by what the
    user can actually walk into right now — not just what exists in the index.

    Args:
        db_conn:    SQLite connection (needed for availability checks)
        filters:    dict of user-specified filter criteria
        avg_stats:  dict of avg preference stats from the personal model
                    (used to decide relax order)
        debug:      print step-by-step trace if True

    Returns:
        tuple(available_ids, relaxed_filters):
            available_ids   – list of currently-available space IDs that
                              matched the (possibly relaxed) filters
            relaxed_filters – the filter dict that produced the results
                              (same as input if no relaxation was needed)
    """
    if not filters:
        return [], filters

    relax_order = _build_relax_order(filters, avg_stats)
    active_filters = filters.copy()

    while True:
        # --- hard filter pass ---
        matching_ids = search_with_filters(active_filters)

        if debug:
            print(f"[progressive] Active filters : {active_filters}")
            print(f"[progressive] Filter matches : {len(matching_ids)} room(s)")

        # --- availability check on this candidate set ---
        available_ids = check_current_availability_window(db_conn, matching_ids)

        if debug:
            print(f"[progressive] Available now  : {len(available_ids)} room(s)")

        if available_ids:
            # We have at least one room that matches the current constraints
            # AND is available right now — no need to relax further.
            if debug:
                relaxed = set(filters.keys()) - set(active_filters.keys())
                if relaxed:
                    print(f"[progressive] Relaxed constraints: {relaxed}")
                else:
                    print("[progressive] All constraints satisfied.")
            return available_ids, active_filters

        # --- nothing available: relax the weakest remaining constraint ---
        if not relax_order:
            if debug:
                print("[progressive] No constraints left to relax. No results found.")
            break

        to_remove = relax_order.pop(0)
        active_filters.pop(to_remove, None)

        if debug:
            print(f"[progressive] Relaxing constraint: '{to_remove}'")

    return [], active_filters


def get_all_study_space_ids(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT study_space_id FROM study_spaces")
    return [row[0] for row in cursor.fetchall()]


def _rank_spaces(space_details, personal_model, user_location):
    """
    Score and sort a list of space detail dicts using the personal model
    and distance from the user's current location.
    """
    available_ids = [s["id"] for s in space_details]
    probability_results = personal_model.probability(available_ids)
    probability_map = {spot_id: score for spot_id, score in probability_results}

    for space in space_details:
        space["score"] = compute_final_score(space, probability_map, user_location)

    return sorted(space_details, key=lambda x: x["score"], reverse=True)


def retrieve_ranked_study_spaces(user_id, filters=None, user_location=None, debug=False):
    """
    Main entry point for retrieving and ranking study spaces.

    Flow
    ----
    1. No filters → return all available rooms ranked purely by proximity.

    2. Filters provided:
       a. Build personal model to get preference stats (used for relax ordering).
       b. Try filters as hard constraints + availability check in one shot.
       c. If results exist → rank with personal model + distance, return.
       d. If no results → progressively relax weakest constraints (one at a time),
          re-checking availability at each step, until rooms are found.
       e. Still nothing → fall back to all available rooms ranked by proximity.
    """
    db_conn = sqlite3.connect(DB_PATH)

    if user_location is None:
        if debug:
            print("[retrieve] No user location provided. Using Aldrich Park default.")
        user_location = {"latitude": 33.6461, "longitude": -117.8427}

    # ------------------------------------------------------------------
    # Step 1: No filters → proximity-only ranking
    # ------------------------------------------------------------------
    if debug:
        print(f'[retrieve] STEP 1')
        
    if not filters or all(v in [None, "", False] for v in filters.values()):
        if debug:
            print("[retrieve] No filters specified. Returning closest available rooms.")

        all_ids = get_all_study_space_ids(db_conn)
        available_ids = check_next_slot_availability_window(db_conn, all_ids)
        space_details = get_space_details(db_conn, available_ids)

        for space in space_details:
            space["score"] = compute_final_score(
                space, probability_map={},
                user_location=user_location,
                prob_weight=0, distance_weight=1
            )
        return sorted(space_details, key=lambda x: x["score"], reverse=True)

    # ------------------------------------------------------------------
    # Step 2: Build personal model (needed for preference stats + scoring)
    # ------------------------------------------------------------------
    if debug:
        print(f'[retrieve] STEP 2')

    personal_model = PersonalModel(user_id, USER_DB=PERSONAL_MODEL_DB_PATH, APP_DB=DB_PATH)
    user_context = personal_model.user_context_for_ranking()
    avg_stats = user_context["average_preference"]

    if debug:
        print(f"[retrieve] User average preference stats: {avg_stats}")

    # ------------------------------------------------------------------
    # Step 3: Hard filter pass with progressive relaxation fallback.
    #
    # progressive_filter_search first tries ALL filters as hard constraints
    # and checks availability. It only relaxes if zero available rooms come
    # back, dropping the weakest constraint each time.
    # ------------------------------------------------------------------
    if debug:
        print(f'[retrieve] STEP 3')

    available_ids, used_filters = progressive_filter_search(
        db_conn, filters, avg_stats, debug=debug
    )

    if debug and used_filters != filters:
        dropped = set(filters.keys()) - set(used_filters.keys())
        print(f"[retrieve] Constraints relaxed to find results: {dropped}")

    # ------------------------------------------------------------------
    # Step 4: Ultimate fallback — if even full relaxation found nothing,
    # return all currently-available rooms so the user always sees something.
    # ------------------------------------------------------------------
    if debug:
        print(f'[retrieve] STEP 4')

    if not available_ids:
        if debug:
            print("[retrieve] No rooms found after full relaxation. Falling back to all available rooms.")

        all_ids = get_all_study_space_ids(db_conn)
        available_ids = check_next_slot_availability_window(db_conn, all_ids)

    if not available_ids:
        if debug:
            print("[retrieve] No rooms available at all.")
        return []

    # ------------------------------------------------------------------
    # Step 5: Fetch details and rank using personal model + distance.
    # Personal model signals always influence ranking regardless of whether
    # we took the direct path or had to relax constraints.
    # ------------------------------------------------------------------
    if debug:
        print(f'[retrieve] STEP 5')
    space_details = get_space_details(db_conn, available_ids)
    ranked_spaces = _rank_spaces(space_details, personal_model, user_location)

    if debug:
        print(f"[retrieve] Returning {len(ranked_spaces)} ranked space(s).")

    return ranked_spaces


def get_available_buildings():
    """Get list of all available buildings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT building_id, name FROM buildings ORDER BY name")
    buildings = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return buildings
