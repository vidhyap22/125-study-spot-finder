from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.get_user_data import return_enriched_study_session_history

def test_get_study_session():
    user_id = 'USER_001'
    print(return_enriched_study_session_history(user_id))


if __name__ == "__main__":
    test_get_study_session()