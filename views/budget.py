import streamlit as st
import pandas as pd
from data import USERS
from utils import render_back_to_menu

def page_budget():
    key = st.session_state.current_user_key
    u = USERS[key]
    st.markdown("## 💰 總預算")

    total = int(u["budget_total"])
    st.metric("預算總額（JPY）", f"¥{total:,}")

    df = pd.DataFrame([{"日期": d, "預算": int(u["day_budget"].get(d, 0))} for d in u["dates"]])
    df["預算"] = df["預算"].map(lambda v: f"¥{v:,}")
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.caption("之後可改成匯入消費明細，自動彙總。")
    render_back_to_menu()
