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


if __name__ == "__main__":
    test_store_filter_info()