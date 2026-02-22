import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.store_personal_model_data import store_filter_info, store_study_session


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

    
if __name__ == "__main__":
    test_store_filter_info()
    test_store_study_session()