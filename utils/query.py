"""
query.py - Search the inverted index and answer user queries
"""

import sqlite3
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "app.db"
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


def get_space_details(space_ids):
    """
    Fetch full details for matching spaces
    
    Args:
        space_ids (list): List of study_space_ids
    
    Returns:
        list: List of dicts with space details
    """
    if not space_ids:
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    
    conn.close()
    
    return results


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance in miles between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate (user location)
        lat2, lon2: Second coordinate (building location)
    
    Returns:
        float: Distance in miles
    """
    R = 3959  # Earth's radius in miles
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def filter_by_distance(space_details, user_lat, user_lon, max_distance_miles):
    """
    Filter spaces by distance from user location
    
    Args:
        space_details (list): List of space detail dicts
        user_lat (float): User's latitude
        user_lon (float): User's longitude
        max_distance_miles (float): Maximum distance in miles
    
    Returns:
        list: Filtered list of space details with distance added
    """
    filtered_spaces = []
    
    for space in space_details:
        building_lat = space["latitude"]
        building_lon = space["longitude"]
        
        if building_lat is not None and building_lon is not None:
            distance = haversine_distance(user_lat, user_lon, building_lat, building_lon)
            
            if distance <= max_distance_miles:
                space["distance"] = round(distance, 2)
                filtered_spaces.append(space)
    
    # Sort by distance
    filtered_spaces.sort(key=lambda x: x["distance"])
    
    return filtered_spaces

def rank_spaces(space_details, filters=None, user_location=None):
    """
    Assign a ranking score to each study space
    
    Higher score = better match
    """

    ranked = []

    for space in space_details:
        score = 0

        # --------------------------
        # Distance scoring
        # --------------------------
        if user_location and "distance" in space:
            # closer = higher score
            score += max(0, 10 - space["distance"])

        # --------------------------
        # Filter preference scoring
        # --------------------------
        if filters:

            if filters.get("tech_enhanced") and space["tech_enhanced"]:
                score += 3

            if filters.get("indoor") and space["indoor"]:
                score += 2

            if filters.get("talking_allowed") == space["talking_allowed"]:
                score += 2

            if filters.get("has_printer") and space["has_printer"]:
                score += 2

            # Capacity preference example
            if filters.get("capacity_range") and space["capacity"]:
                try:
                    low, high = map(int, filters["capacity_range"].split('-'))
                    if low <= space["capacity"] <= high:
                        score += 3
                except:
                    pass

        # Availability bonus
        if not space["must_reserve"]:
            score += 1

        space["score"] = round(score, 2)
        ranked.append(space)

    # Sort descending by score
    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked


def get_available_rooms(start_time=None, end_time=None):
    """
    Get rooms available during a specific time window
    
    Args:
        start_time (str): ISO format datetime (optional)
        end_time (str): ISO format datetime (optional)
    
    Returns:
        list: Study space IDs that are available
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if start_time and end_time:
        # Find rooms with NO conflicting unavailable bookings
        cursor.execute("""
        SELECT DISTINCT study_space_id
        FROM room_availability
        WHERE is_available = 1
        AND start_time >= ?
        AND end_time <= ?
        AND datetime(scraped_at) > datetime('now', '-24 hours')
    """, (start_time, end_time))
    else:
        # Get all rooms that require reservation
        cursor.execute("""
            SELECT study_space_id
            FROM study_spaces
            WHERE must_reserve = 1
        """)
    
    available_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return available_ids


def query_study_spaces(filters=None, user_location=None, max_distance=None, 
                       check_availability=False, start_time=None, end_time=None):
    """
    Updated query function with availability checking
    """
    # Step 1: Apply filters using inverted index
    if filters:
        matching_ids = search_with_filters(filters)
        print("matching_ids from filters:", len(matching_ids))
        if not matching_ids:
            return []
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT study_space_id FROM study_spaces")
        matching_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
    
    # Step 2: Filter by availability if requested
    if check_availability and start_time and end_time:
        available_ids = get_available_rooms(start_time, end_time)
        print("available_ids:", len(available_ids))
        matching_ids = list(set(matching_ids) & set(available_ids))
        if not matching_ids:
            print('intersection was empty')
            return []            
    
    # Step 3: Get full details
    space_details = get_space_details(matching_ids)
    
    # Step 4: Apply distance filter
    if user_location and max_distance:
        user_lat = user_location.get("latitude")
        user_lon = user_location.get("longitude")
        if user_lat and user_lon:
            space_details = filter_by_distance(
                space_details,
                user_lat,
                user_lon,
                max_distance
            )

    # Step 5: Rank results
    space_details = rank_spaces(
        space_details,
        filters=filters,
        user_location=user_location
    )

    return space_details

def get_available_buildings():
    """Get list of all available buildings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT building_id, name FROM buildings ORDER BY name")
    buildings = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return buildings