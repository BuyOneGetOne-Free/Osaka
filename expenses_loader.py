# expenses_loader.py
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
EXP_PATH = DATA_DIR / "expenses.csv"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

SCHEMA = ["id","user_key","date","time","amount_jpy","category","note","activity_title","link"]

def load_expenses() -> pd.DataFrame:
    if EXP_PATH.exists():
        df = pd.read_csv(EXP_PATH, dtype=str).fillna("")
    else:
        df = pd.DataFrame(columns=SCHEMA)
    # 型別整理
    if "amount_jpy" in df.columns:
        df["amount_jpy"] = pd.to_numeric(df["amount_jpy"], errors="coerce").fillna(0).astype(int)
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    return df[SCHEMA]

def _next_id(df: pd.DataFrame) -> int:
    return (df["id"].max() + 1) if len(df) else 1

def backup():
    if EXP_PATH.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        (BACKUP_DIR / f"expenses_{ts}.csv").write_bytes(EXP_PATH.read_bytes())

def add_expense(user_key: str, date: str, time: str, amount_jpy: int,
                category: str, note: str, activity_title: str = "", link: str = ""):
    df = load_expenses()
    new_id = _next_id(df)
    row = {
        "id": new_id,
        "user_key": user_key,
        "date": str(date).strip(),
        "time": str(time or "").strip(),
        "amount_jpy": int(amount_jpy),
        "category": str(category or "").strip(),
        "note": str(note or "").strip(),
        "activity_title": str(activity_title or "").strip(),
        "link": str(link or "").strip(),
    }
    backup()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(EXP_PATH, index=False, encoding="utf-8")
    return new_id

def save_expenses(df: pd.DataFrame):
    """整張表覆蓋儲存（提供在頁面用 data_editor 編修後寫回）"""
    backup()
    # 保型別
    if "amount_jpy" in df.columns:
        df["amount_jpy"] = pd.to_numeric(df["amount_jpy"], errors="coerce").fillna(0).astype(int)
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df = df[SCHEMA]
    df.to_csv(EXP_PATH, index=False, encoding="utf-8")
