import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from utils.query import query_study_spaces

def run_tests():

    print("\n===== TEST 1: Basic Filters =====")

    filters = {
        "capacity_range": "1-4",
        "indoor": True,
        "tech_enhanced": False,
        "talking_allowed": True
    }

    results = query_study_spaces(filters=filters)

    print(f"Found {len(results)} spaces")

    for space in results[:5]:
        print(space)


    print("\n===== TEST 2: Distance Filtering =====")

    user_location = {
        "latitude": 33.646,
        "longitude": -117.842
    }

    results = query_study_spaces(
        filters={"indoor": True},
        user_location=user_location,
        max_distance=0.5
    )

    print(f"Nearby results: {len(results)}")

    for space in results[:5]:
        print(space)


    print("\n===== TEST 3: Availability =====")

    results = query_study_spaces(
    filters={"indoor": True},
    check_availability=True,
    start_time="2026-02-09T10:00:00-08:00",
    end_time="2026-02-09T10:30:00-08:00"
    )

    print(f"Available rooms: {len(results)}")

    for space in results[:5]:
        print(space)


if __name__ == "__main__":
    run_tests()
