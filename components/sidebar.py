import streamlit as st
import time
from components.custom_html import get_digital_human_html
from services.blockchain import record_to_blockchain

def render_sidebar():
    with st.sidebar:
        st.markdown(get_digital_human_html(), unsafe_allow_html=True)
        st.markdown("### ⚙️ 业务终端切换")
        user_role = st.selectbox("👤 切换操作视角", ["👑 管理员：决策指挥舱", "👨‍ 巡检员：执行作战端", "📢 社会公众：参与激励端"])
        target_obj = st.selectbox("🎯 指标切换", ["酸碱", "溶解氧", "氨氮", "总磷", "浊度"])
        ml_algorithm = st.radio("🧠 预测模型", ["RF (随机森林)", "GBDT (梯度提升树)", "DT (决策树)", "SVR (支持向量机)", "MLP (神经网络)", "KNN (K近邻)"])
        future_days = st.slider("📅 推演天数", 3, 14, 7)
        start_btn = st.button("🚀 启动全域 AI 推演", type="primary", use_container_width=True)

        if st.button("🚨 模拟突发污染 (触发AI联动)", use_container_width=True):
            st.session_state['god_mode'] = True
            st.session_state.pop('future_vals', None)
            record_to_blockchain("物联网传感器 (Z2节点)", "自动上报异常读数", "预警：监测到下游水质严重恶化，指标突破红线")
            time.sleep(0.05)
            record_to_blockchain("AI 智能决策中枢", "下发物理阀门锁死指令", "决策：接管底层硬件，物理切断 Z2 闸门(开度降至0%)以阻断污染源")
            st.rerun()

        if st.button("🔄 解除预警与锁定", use_container_width=True):
            st.session_state['god_mode'] = False
            st.session_state.pop('future_vals', None)
            record_to_blockchain("管理员(指挥舱)", "人工解除警戒状态", "恢复全域水网常态化循环调度")
            st.rerun()

        if st.button("🚨 多模态AI研判", use_container_width=True):
            st.session_state['citizen_report'] = True

        return user_role, target_obj, ml_algorithm, future_days, start_btn