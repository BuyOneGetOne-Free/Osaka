import streamlit as st
from data import USERS
from utils import render_back_to_menu

def page_checklist():
    key = st.session_state.current_user_key
    u = USERS[key]
    display_name = u["display_name"]

    st.markdown(f"### 🧾 出發前準備（{display_name}）")
    st.caption("勾一勾就安心！")

    st.session_state.check_state.setdefault(key, {})
    check_map = st.session_state.check_state[key]

    for item in u["checklist"]:
        default = check_map.get(item, False)
        checked = st.checkbox(item, value=default, key=f"chk_{key}_{item}")
        check_map[item] = checked

    st.markdown("---")
    all_done = all(check_map.get(item, False) for item in u["checklist"])
    colA, colB = st.columns([2, 1])
    with colA:
        st.info("全部打勾後再按按鈕會有驚喜 ✨")
    with colB:
        if st.button("🎉 我都準備好了！", use_container_width=True, key=f"btn_ready_{key}"):
            if all_done:
                st.success("太棒了！全部完成 ✅")
                st.balloons()
            else:
                st.warning("還有東西沒打勾喔～")

    render_back_to_menu()
