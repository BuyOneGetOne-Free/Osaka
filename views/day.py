import streamlit as st
from datetime import datetime
from data import USERS
from utils import budget_badge, render_back_to_menu
from expenses_loader import load_expenses

# ========== 樣式：放大字體 / 行高 / 連結樣式 ==========
CSS = """
<style>
.itin-section h3 { margin-top: 1.5rem; }          /* 標題大小不動 */

/* 清單容器 */
.itin-list { list-style: disc; margin-left: 1.2rem; padding-left: 0.8rem; }

/* ✅ 只放大清單內文；提高選擇器權重 + !important */
.stMarkdown ul.itin-list > li.itin-item {
  font-size: 1.35rem !important;
  line-height: 2.0rem !important;
  margin: 0.25rem 0 !important;
}

/* 讓時間/標題/細節/連結都繼承 li 的字級 */
.stMarkdown ul.itin-list > li.itin-item * {
  font-size: inherit !important;
}

.itin-time  { font-weight: 600; margin-right: .4rem; }
.itin-title { font-weight: 700; }
.itin-detail { color: #444; }

/* 連結樣式 */
.itin-link a { text-decoration: none; border-bottom: 1px dashed #888; }
.itin-link a:hover { border-bottom-color: #333; }
</style>
"""



# ========== 小工具 ==========
def _fmt_time(s: str) -> str:
    """容錯：'9:5' -> '09:05'；空值回空字串"""
    s = (s or "").strip()
    if not s:
        return ""
    parts = s.split(":")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        h = int(parts[0]); m = int(parts[1])
        return f"{h:02d}:{m:02d}"
    return s

def _date_to_md(s: str) -> str:
    """把 'YYYY-MM-DD' 或 'M/D' 轉為 'M/D'（顯示/比對用）"""
    s = (s or "").strip()
    if not s:
        return ""
    for fmt in ("%Y-%m-%d", "%m/%d", "%-m/%-d"):
        try:
            dt = datetime.strptime(s, fmt)
            return f"{dt.month}/{dt.day}"
        except Exception:
            continue
    return s  # 解析不了就原樣

def _render_segment(title: str, items):
    st.markdown(f'<div class="itin-section"><h3>{title}</h3></div>', unsafe_allow_html=True)
    if not items:
        st.info("（尚未安排）")
        return
    html = ['<ul class="itin-list">']
    for it in items:
        # 兼容舊資料（若是純字串）
        if isinstance(it, str):
            html.append(f'<li class="itin-item">{it}</li>')
            continue
        t1 = _fmt_time(it.get("start_time", ""))
        t2 = _fmt_time(it.get("end_time", ""))
        time_str = f'<span class="itin-time">[{t1}-{t2}]</span>' if (t1 or t2) else ""
        title_html = f'<span class="itin-title">{it.get("title","").strip()}</span>'
        detail = it.get("detail","").strip()
        detail_html = f' <span class="itin-detail">｜{detail}</span>' if detail else ""
        link = it.get("link","").strip()
        link_html = f' <span class="itin-link"> · <a href="{link}" target="_blank">查看更多</a></span>' if link else ""
        html.append(f'<li class="itin-item">{time_str}{title_html}{detail_html}{link_html}</li>')
    html.append("</ul>")
    st.markdown("\n".join(html), unsafe_allow_html=True)

# ========== 主頁面 ==========
def page_day():
    st.markdown(CSS, unsafe_allow_html=True)

    key = st.session_state.get("current_user_key")
    if not key:
        st.warning("請先返回主畫面選擇使用者")
        render_back_to_menu()
        return

    u = USERS[key]
    d = st.session_state.get("selected_date")
    if d is None:
        st.warning("尚未選擇日期")
        render_back_to_menu()
        return

    # 標題
    st.markdown(f"## 📅 {d} 行程")

    # 當日預算
    budget = int(u["day_budget"].get(d, 0))

    # 當日花費（從 expenses.csv 讀），支援 YYYY-MM-DD 或 M/D 比對
    df_exp = load_expenses()
    if len(df_exp):
        exp_view = df_exp.copy()
        exp_view["date_view"] = exp_view["date"].map(_date_to_md)
        spent = int(
            exp_view[
                (exp_view["user_key"] == key) & (exp_view["date_view"] == d)
            ]["amount_jpy"].sum()
        )
    else:
        spent = 0

    # 只保留「吸頂」那組指標（避免重複顯示）
    st.markdown('<div class="sticky-bar block-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("當日預算", f"¥{budget:,}")
    with col2:
        remaining = budget - spent
        st.metric("當日花費", f"¥{spent:,}", delta=f"剩餘 ¥{remaining:,}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("— 使用下方分頁查看不同时段內容 —")

    # 分頁
    tabs = st.tabs(["🧢 早上", "🌞 中午", "🌙 晚上"])
    day = u["activities"].get(d, {"morning": [], "noon": [], "night": []})

    with tabs[0]:
        _render_segment("早上", day.get("morning", []))

    with tabs[1]:
        _render_segment("中午/下午", day.get("noon", []))

    with tabs[2]:
        _render_segment("晚上", day.get("night", []))

    st.markdown("---")
    render_back_to_menu()
