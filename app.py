import streamlit as st
from config import settings

# 必须放在脚本第一行
st.set_page_config(page_title=settings.PAGE_TITLE, layout=settings.LAYOUT, initial_sidebar_state=settings.SIDEBAR_STATE)

from services.blockchain import init_blockchain_state
from services.data_loader import load_timeseries_data, load_geo_data
from components.sidebar import render_sidebar
from views import public_view, inspector_view, admin_view

# 加载分离的 CSS 样式
with open('config/style.css', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 初始化全局状态
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'god_mode' not in st.session_state:
    st.session_state['god_mode'] = False
init_blockchain_state()

# 统一加载数据
df = load_timeseries_data(st.session_state['god_mode'])
geo_df = load_geo_data(st.session_state['god_mode'])

# 页面顶部标题
st.markdown("<div class='datav-header'><h1 class='datav-title'>全 民 智 水 · 多 模 态 AI 治 水 终 端</h1></div>", unsafe_allow_html=True)

# 渲染侧边栏并获取所有配置状态
user_role, target_obj, ml_algorithm, future_days, start_btn = render_sidebar()

# 路由分发机制
if user_role == "📢 社会公众：参与激励端":
    public_view.render_public_view(geo_df)
elif user_role == "👨‍ 巡检员：执行作战端":
    inspector_view.render_inspector_view()
elif user_role == "👑 管理员：决策指挥舱":
    admin_view.render_admin_view(df, geo_df, target_obj, ml_algorithm, future_days, start_btn)