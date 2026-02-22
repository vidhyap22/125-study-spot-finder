import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.store_personal_model_data import add_user, delete_bookmarks, store_bookmarks, store_filter_info, store_spot_feedback, store_spot_view, store_study_session


def test_store_filter_info():
    fake_filter = {
        "min_capacity": 2,
        "max_capacity": 6,
        "tech_enhanced": 1,        
        "has_printer": 0,
        "is_indoor": 1,
        "is_talking_allowed": 0
    }

    store_filter_info("USER_001", fake_filter, debug=True)

def test_store_study_session():
    fake_session_1 = {
        "study_space_id": 44696,   # LLIB 3rd Floor - Collaboration Zone
        "building_id": "LLIB",
        "started_at": "10:23",
        "ended_at": "13:45",
        "start_date": "2026-02-09",
        "end_date": "2026-02-09",
        "duration_ms": 3 * 60 * 60 * 1000 + 22 * 60 * 1000,  
        "ended_reason": "user_left"
    }

    store_study_session("USER_001", fake_session_1, debug=True)

def test_store_bookmarks():
    fake_data = {
        "study_space_id": 44668,
        "building_id": "SLIB",
        "created_at": "2026-02-22 17:45:00"
    }
    store_bookmarks("USER_001", fake_data, debug=True)

def test_delete_bookmarks():
    fake_data = {
        "study_space_id": 44668,
        "building_id": "SLIB",
    }
    delete_bookmarks("USER_001", fake_data, debug=True)

def test_store_spot_view():
    fake_data_1 = {
    "study_space_id": 44668,
    "building_id": "SLIB",
    "opened_at": "2026-02-22 17:30:00",
    "closed_at": "2026-02-22 17:35:30",
    "dwell_ms": 330000,
    "source": "recommendation",
    "list_rank": 2
    }

    store_spot_view("USER_001", fake_data_1, True)

    fake_data_2 = {
        "study_space_id": 44696,
        "building_id": "LLIB",
        "opened_at": "2026-02-22 18:30:00",
        "closed_at": "2026-02-22 18:35:30",
        "dwell_ms": 330000,
    }
    store_spot_view("USER_001", fake_data_2, True)
    
def test_store_spot_feedback():
    fake_feedback = {
    "study_space_id": 44701,
    "building_id": "LLIB",
    "rating": 1,
    "updated_at": "2026-02-22 18:35:42"
    }
    store_spot_feedback("USER_001", fake_feedback, True)

def test_add_user():
    fake_user_data = {
    "created_at": "2026-02-22 19:15:00"
    }
    add_user("USER_003", fake_user_data, True)

if __name__ == "__main__":
    test_store_filter_info()
    test_store_study_session()
    test_store_bookmarks()
    test_delete_bookmarks()
    test_store_spot_view()
    test_store_spot_feedback()
    test_add_user()