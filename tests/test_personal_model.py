import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from personal_model.personal_model_process import PersonalModel

BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
APP_DB = BASE_DIR / "data" / "database" / "app.db"

def test_user_1():
    user1 = PersonalModel("USER_001", USER_DB, APP_DB)
    user1.user_context_for_ranking()
    result = user1.probability([44672, 34681])
    print(result)

def test_user_2():
    user2 = PersonalModel("USER_002", USER_DB, APP_DB)
    user2.user_context_for_ranking()
    result = user2.probability([44672, 34681])
    print(result)

def test_user_7_edgecase():
    user7 = PersonalModel("USER_007", USER_DB, APP_DB)
    user_context = user7.user_context_for_ranking()
    average_preference = user_context["average_preference"]
    print("average preference: ", '\n', average_preference)
    result = user7.probability([44672, 34681])
    print(result)

def main():
    #print('='*50, "user7", '='*50)
    #test_user_1()
    #print('='*50, "user2", '='*50)
    #test_user_2()
    print('='*50, "user7", '='*50)
    test_user_7_edgecase()

if __name__ == '__main__':
    main()