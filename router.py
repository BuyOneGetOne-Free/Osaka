import streamlit as st
from utils import ensure_state, switch_user_sidebar
from views.home import page_home
from views.user_menu import page_user_menu
from views.checklist import page_checklist
from views.day import page_day
from views.budget import page_budget
from utils import reload_data_button  # 加這行
from views.expenses import page_expenses
ROUTES = {
    "home": page_home,
    "user_menu": page_user_menu,
    "checklist": page_checklist,
    "day": page_day,
    "budget": page_budget,
    "expenses": page_expenses,
}


def run_app():
    ensure_state()
    switch_user_sidebar()
    reload_data_button()  # 顯示「重新載入資料」
    ROUTES[st.session_state.route]()