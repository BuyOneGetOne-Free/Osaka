import streamlit as st
from utils import pick_user

def page_home():
    st.title("歡迎來到大阪行前說明網站！")
    st.subheader("你是誰？")

    col1, col2 = st.columns(2) 
    with col1:
        st.markdown("#### ➊ 我是：請輸入新名稱")
        if st.button("➡️ 進入『請輸入新名稱』的專屬頁面", use_container_width=True, key="btn_user_custom"):
            pick_user("a")

    with col2:
        st.markdown("#### ➋ 我是：冰箱沒關好")
        if st.button("➡️ 進入『冰箱沒關好』的專屬頁面", use_container_width=True, key="btn_user_fridge"):
            pick_user("b")

    st.divider()
