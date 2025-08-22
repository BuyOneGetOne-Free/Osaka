from data_loader import load_users, load_checklist, load_budget, load_activities, build_users_dict

def load_ALL_USERS():
    users_df = load_users("data/users.csv")
    checklist_df = load_checklist("data/checklist.csv")
    budget_df = load_budget("data/budget.csv")
    acts_df = load_activities("data/activities.csv")
    return build_users_dict(users_df, checklist_df, budget_df, acts_df)

# 舊程式會 from data import USERS
# 改成在 import 時就讀一次（也可以在 router 開頁時重載）
USERS = load_ALL_USERS()
