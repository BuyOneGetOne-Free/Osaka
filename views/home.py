import streamlit as st
from utils import pick_user
import random

# 一些與大阪/京都/奈良/交通/美食相關的輕量提示
TIPS = [
    "道頓堀最晚人潮通常在 19:00–21:00，想拍空景可以提早或更晚一點走。",
    "黑門市場早上魚貨較新鮮、人也少；想慢慢逛可以選 9–10 點。",
    "如果按不到配件或是極限威能，可以在虛擬搖桿設定中放大你的按鍵。",
    "奈良鹿會點頭多半是在討餅，拿餅時請把袋子收好，避免被搶。",
    "如果你的鹿仙貝被搶走了，不要猶豫，直接處決那頭鹿。"
    "道頓堀的大火疑似是Donki企鵝放的",
    "不管事走路還是手扶梯都要靠左行駛。",
    "章魚燒外脆內軟的關鍵是高含水麵糊與高溫鐵板，現做現吃口感最好。",
    "如果有免稅/退稅的店，可以登入visit japan或是直接刷護照",
    "想省流量可事先把離線地圖下載好（地鐵圖 + 景點周邊）。",
    "熱門甜點店常有排隊，若行程彈性，把甜點安排在午餐與晚餐之間的離峰時段。",
    "日本的腳踏車多到連麥當勞歡樂頌都是用腳踏車。",
    "Donki企鵝是南極出生，東京長大的企鵝。",
    "飛田新地是飛牛牧場在日本的分店",
    "如果想要來一份清爽的甜點，不如來份英花刺身!",
]

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
    # === 這一段就是「只在 Home 顯示」的小提示按鈕 ===
    st.markdown("#### 🎁 小彩蛋")
    col1, col2 = st.columns([2,1])

    # 第一次抽或點「換一則」都會重抽
    with col1:
        if st.button("你知道嗎？抽一則小提示", key="btn_tip_draw", use_container_width=True):
            st.session_state["home_tip"] = random.choice(TIPS)

    with col2:
        if st.session_state.get("home_tip"):
            if st.button("換一則", key="btn_tip_redraw", use_container_width=True):
                st.session_state["home_tip"] = random.choice(TIPS)

    # 顯示目前抽到的小提示
    tip = st.session_state.get("home_tip")
    if tip:
        st.success(f"💡 {tip}")
