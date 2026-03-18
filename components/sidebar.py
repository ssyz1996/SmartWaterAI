import streamlit as st
import time
from components.custom_html import get_digital_human_html
from services.blockchain import record_to_blockchain


def render_sidebar():
    with st.sidebar:
        st.markdown(get_digital_human_html(), unsafe_allow_html=True)
        # ===== 新增：湖仓一体大数据控制台 =====
        with st.expander("🗄️ 湖仓一体大数据引擎底座", expanded=True):
            st.caption("动态操作 Parquet 数据湖，体验毫秒级 OLAP 聚合")
            st.session_state['db_interval'] = st.selectbox(
                "⏳ 动态降采样粒度 (Group By)",
                ["1 hour", "6 hours", "12 hours", "1 day", "7 days"],
                index=1
            )
            st.session_state['db_limit'] = st.slider(
                "📊 扫描输出节点数 (Limit)",
                min_value=30, max_value=500, value=90, step=10
            )
        st.markdown("---")
        # =====================================
        st.markdown("### ⚙️ 业务终端切换")
        user_role = st.selectbox("👤 切换操作视角",
                                 ["👑 管理员：决策指挥舱", "👨‍ 巡检员：执行作战端", "📢 社会公众：参与激励端"])
        target_obj = st.selectbox("🎯 指标切换", ["酸碱", "溶解氧", "氨氮", "总磷", "浊度"])
        ml_algorithm = st.radio("🧠 预测模型", ["RF (随机森林)", "GBDT (梯度提升树)", "DT (决策树)", "SVR (支持向量机)",
                                               "MLP (神经网络)", "KNN (K近邻)"])
        future_days = st.slider("📅 推演天数", 3, 14, 7)
        start_btn = st.button("🚀 启动全域 AI 推演", type="primary", use_container_width=True)

        if st.button("🔄 解除预警与锁定", use_container_width=True):
            st.session_state['god_mode'] = False
            st.session_state.pop('future_vals', None)
            record_to_blockchain("管理员(指挥舱)", "人工解除警戒状态", "恢复全域水网常态化循环调度")
            st.rerun()

        if st.button("🚨 多模态AI研判", use_container_width=True):
            st.session_state['citizen_report'] = True

        # ==========================================
        # ✨ 新增：针对折叠面板的 CSS 样式优化，让其对齐并放大字体
        # ==========================================
        st.markdown("""
        <style>
            /* 1. 修改折叠面板标题的字体大小和粗细，对齐普通按钮 */
            [data-testid="stSidebar"] [data-testid="stExpander"] summary p {
                font-size: 16px !important;
                font-weight: 500 !important;
            }
            /* 2. 去除原生折叠面板外面的灰色边框，显得更干净 */
            [data-testid="stSidebar"] [data-testid="stExpander"] details {
                border: none !important;
            }
            /* 3. 取消折叠面板默认的左侧缩进，让它和上面的按钮左边缘完全对齐 */
            [data-testid="stSidebar"] [data-testid="stExpander"] summary {
                padding-left: 0rem !important;
                padding-right: 0rem !important;
            }
        </style>
        """, unsafe_allow_html=True)
        # ==========================================

        # 1. 新增一个默认折叠的面板，取一个专业的名字
        with st.expander("🛠️ 开发者工具", expanded=False):

            # 2. 把按钮放在这个折叠面板里面
            if st.button("极端气象模拟预演", use_container_width=True):
                st.session_state['god_mode'] = True
                st.session_state.pop('future_vals', None)
                record_to_blockchain("物联网传感器 (Z2节点)", "自动上报异常读数",
                                     "预警：监测到下游水质严重恶化，指标突破红线")
                time.sleep(0.05)
                record_to_blockchain("AI 智能决策中枢", "下发物理阀门锁死指令",
                                     "决策：接管底层硬件，物理切断 Z2 闸门(开度降至0%)以阻断污染源")
                st.rerun()

        return user_role, target_obj, ml_algorithm, future_days, start_btn