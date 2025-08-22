import streamlit as st
from data import load_ALL_USERS
def ensure_state():
    if "route" not in st.session_state:
        st.session_state.route = "home"  # home / user_menu / checklist / day / budget
    if "current_user_key" not in st.session_state:
        st.session_state.current_user_key = None
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    if "check_state" not in st.session_state:
        st.session_state.check_state = {}  # {user_key: {item_text: bool}}

def go(route: str):
    st.session_state.route = route
    st.rerun()

def pick_user(user_key: str):
    st.session_state.current_user_key = user_key
    go("user_menu")

def render_back_to_menu():
    if st.button("⬅️ 回我的選單", use_container_width=True, key="back_to_menu"):
        go("user_menu")

def budget_badge(amount: int | float):
    st.markdown(f"**當日預算：** ¥{int(amount):,}")

def switch_user_sidebar():
    # 全域側邊欄上的「切換使用者」按鈕（除了首頁都顯示）
    if st.session_state.route != "home":
        with st.sidebar:
            if st.button("🙋 切換使用者", use_container_width=True, key="switch_user"):
                # 清掉當前使用者與日期再回首頁
                st.session_state.current_user_key = None
                st.session_state.selected_date = None
                go("home")



def reload_data_button():
    with st.sidebar:
        if st.button("🔄 重新載入資料", use_container_width=True, key="reload_data"):
            from data import USERS
            new_users = load_ALL_USERS()
            USERS.clear()
            USERS.update(new_users)
            st.success("資料已重新載入")
            st.rerun()
