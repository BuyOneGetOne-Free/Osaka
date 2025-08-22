# views/expenses.py
import streamlit as st
import pandas as pd
from expenses_loader import load_expenses, add_expense, save_expenses
from utils import render_back_to_menu

CATEGORIES = ["餐飲", "交通", "門票", "住宿", "購物", "其他"]

def page_expenses():
    key = st.session_state.get("current_user_key")
    if not key:
        st.warning("請先選擇使用者")
        return

    st.markdown("## 🧾 記帳")
    st.caption("新增支出、查看與編修你的消費紀錄；所有資料儲存在 data/expenses.csv。")

    # ---------- 新增一筆 ----------
    with st.expander("新增一筆支出", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            date = st.text_input("日期（YYYY-MM-DD 或 M/D）", value="")
            time = st.text_input("時間（HH:MM，可空）", value="")
            amount = st.number_input("金額（JPY）", min_value=0, step=100, value=0)
        with c2:
            category = st.selectbox("分類", options=CATEGORIES, index=len(CATEGORIES)-1)
            activity = st.text_input("對應行程（可空）", value="")
        with c3:
            link = st.text_input("連結（可空）", value="")
            note = st.text_area("備註（可空）", height=58)

        if st.button("➕ 新增", type="primary", use_container_width=True):
            if not date or amount <= 0:
                st.warning("請填日期與金額")
            else:
                new_id = add_expense(key, date, time, amount, category, note, activity, link)
                st.success(f"已新增記帳（id={new_id}）")
                st.rerun()

    st.markdown("---")

    # ---------- 檢視 / 編修 ----------
    df_all = load_expenses()
    df_user = df_all[df_all["user_key"] == key].copy().sort_values("id").reset_index(drop=True)

    # 快速篩選日期
    colA, colB = st.columns([2, 1])
    with colA:
        q_date = st.text_input("只看某日期（例如 9/1 或 2025-09-01；可留空）", value="")
    with colB:
        if q_date.strip():
            df_user = df_user[df_user["date"].astype(str).str.strip() == q_date.strip()]

    # 小計與空資料處理（無論如何都畫返回鈕）
    total = int(df_user["amount_jpy"].sum()) if len(df_user) else 0
    st.metric("目前篩選金額小計", f"¥{total:,}")

    if len(df_user) == 0:
        st.info("尚無紀錄或篩選無資料")
        st.markdown("---")
        render_back_to_menu()
        return

    st.write("### 我的消費紀錄")
    edited = st.data_editor(
        df_user,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        column_order=["id", "date", "time", "amount_jpy", "category",
                      "note", "activity_title", "link", "user_key"],
        column_config={
            "id": st.column_config.NumberColumn("id", disabled=True),
            "user_key": st.column_config.TextColumn("user_key", disabled=True),  # 避免誤改
            "amount_jpy": st.column_config.NumberColumn("amount_jpy", step=100, min_value=0),
        },
        key="exp_editor",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 儲存所有修改", use_container_width=True):
            # 只更新屬於此使用者的列；其他人的資料保持原樣
            others = df_all[df_all["user_key"] != key]
            combined = pd.concat([others, edited], ignore_index=True)
            save_expenses(combined)
            st.success("已儲存到 data/expenses.csv")
            st.rerun()

    with c2:
        st.download_button(
            "⬇️ 匯出目前篩選為 CSV",
            data=edited.to_csv(index=False).encode("utf-8"),
            file_name="expenses_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")
    render_back_to_menu()
