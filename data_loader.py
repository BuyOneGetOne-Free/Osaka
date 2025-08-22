import pandas as pd
from datetime import datetime
from typing import Dict, Any

DATE_FORMATS = ["%Y-%m-%d", "%m/%d", "%-m/%-d"]  # Windows 可能不支援 %-m，可用 try/except

def _parse_date(val: str) -> str:
    if pd.isna(val) or str(val).strip() == "":
        return ""
    s = str(val).strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            # 顯示用 M/D（不補零）
            return f"{dt.month}/{dt.day}"
        except Exception:
            continue
    # 解析失敗，原樣返回（之後驗證會抓到）
    return s

def _to_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    return s in ["1", "true", "yes", "y", "t"]

def load_users(path="data/users.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    if not {"user_key","display_name","enabled"}.issubset(df.columns):
        raise ValueError("users.csv 欄位需包含：user_key, display_name, enabled")
    df["enabled"] = df["enabled"].map(_to_bool)
    df = df[df["enabled"] == True]
    return df[["user_key","display_name"]].reset_index(drop=True)

def load_checklist(path="data/checklist.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    req = {"user_key","item","required","default_checked"}
    if not req.issubset(df.columns):
        raise ValueError("checklist.csv 欄位需包含：user_key,item,required,default_checked")
    df["required"] = df["required"].map(_to_bool)
    df["default_checked"] = df["default_checked"].map(_to_bool)
    return df

def load_budget(path="data/budget.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    req = {"user_key","date","day_budget_jpy"}
    if not req.issubset(df.columns):
        raise ValueError("budget.csv 欄位需包含：user_key,date,day_budget_jpy（可選 total_budget_jpy）")
    df["date_view"] = df["date"].map(_parse_date)
    # 整數轉換
    for col in ["day_budget_jpy","total_budget_jpy"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df

def load_activities(path="data/activities.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    req = {"user_key","date","segment","order","title","detail","start_time","end_time","cost_jpy","link"}
    if not req.issubset(df.columns):
        raise ValueError("activities.csv 欄位需包含：" + ",".join(sorted(req)))
    df["date_view"] = df["date"].map(_parse_date)
    df["order"] = pd.to_numeric(df["order"], errors="coerce").fillna(0).astype(int)
    # 整數/浮點
    for col in ["cost_jpy"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    # 驗證 segment
    ok_seg = {"morning","noon","night"}
    bad = df[~df["segment"].isin(ok_seg)]
    if len(bad) > 0:
        raise ValueError(f"activities.csv 有不合法的 segment：{bad['segment'].unique().tolist()}（合法：morning/noon/night）")
    return df

def build_users_dict(users_df, checklist_df, budget_df, acts_df):
    """
    產生：
    USERS[user_key] = {
      display_name, dates[], budget_total, day_budget{M/D:int},
      checklist: [str, ...],
      activities: { "M/D": {
          "morning": [ {title, detail, start_time, end_time, link, cost_jpy}, ... ],
          "noon":    [ ... ],
          "night":   [ ... ],
      }}
    }
    """
    users = {}
    for r in users_df.itertuples():
        users[r.user_key] = {
            "display_name": r.display_name,
            "dates": [],
            "budget_total": 0,
            "day_budget": {},
            "checklist": [],
            "activities": {},
        }

    # checklist
    for r in checklist_df.itertuples():
        if r.user_key in users:
            users[r.user_key]["checklist"].append(r.item)

    # budget（每日 + 總額）
    if "date_view" not in budget_df.columns:
        budget_df = budget_df.copy()
        from datetime import datetime
        def _d(v):
            s = str(v).strip()
            for fmt in ("%Y-%m-%d", "%m/%d"):
                try:
                    dt = datetime.strptime(s, fmt)
                    return f"{dt.month}/{dt.day}"
                except Exception:
                    pass
            return s
        budget_df["date_view"] = budget_df["date"].map(_d)

    for r in budget_df.itertuples():
        if r.user_key not in users: 
            continue
        if r.date_view:
            users[r.user_key]["dates"].append(r.date_view)
            users[r.user_key]["day_budget"][r.date_view] = int(getattr(r, "day_budget_jpy", 0))
        if hasattr(r, "total_budget_jpy") and int(getattr(r, "total_budget_jpy", 0)) > 0:
            users[r.user_key]["budget_total"] = int(r.total_budget_jpy)

    # activities（關鍵：保留時間與連結）
    acts_sorted = acts_df.sort_values(["user_key","date_view","segment","order"])
    for r in acts_sorted.itertuples():
        if r.user_key not in users or not r.date_view:
            continue
        day = users[r.user_key]["activities"].setdefault(
            r.date_view, {"morning": [], "noon": [], "night": []}
        )
        item = {
            "title": str(r.title).strip(),
            "detail": str(r.detail).strip(),
            "start_time": str(r.start_time).strip(),
            "end_time": str(r.end_time).strip(),
            "link": str(r.link).strip(),
            "cost_jpy": int(pd.to_numeric(getattr(r, "cost_jpy", 0), errors="coerce") or 0),
        }
        day[str(r.segment)].append(item)

    # 日期排序去重
    for u in users.values():
        u["dates"] = sorted(list(dict.fromkeys(u["dates"])),
                            key=lambda s: (int(s.split("/")[0]), int(s.split("/")[1])))
    return users
