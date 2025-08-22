import streamlit as st
from data import USERS
from utils import go

def page_user_menu():
    key = st.session_state.current_user_key
    u = USERS[key]
    display_name = u["display_name"]

    st.title(f"👋 哈囉，{display_name}")
    st.caption("請選擇你要看的內容")

    # user_menu.py 內，原本的三顆按鈕區塊改成：
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown("#### 快速操作")
    act1, act2, act3 = st.columns([1,1,1])
    with act1:
        if st.button("🧾 出發前準備", use_container_width=True): go("checklist")
    with act2:
        if st.button("💰 總預算", use_container_width=True): go("budget")
    with act3:
        if st.button("🧮 記帳", use_container_width=True): go("expenses")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### 📅 行程日期")
    grid_cols = st.columns(4)  # 四欄看起來更整齊
    for i, d in enumerate(u["dates"]):
        with grid_cols[i % 4]:
            if st.button(d, use_container_width=True, key=f"daybtn_{key}_{d}"):
                st.session_state.selected_date = d
                go("day")


