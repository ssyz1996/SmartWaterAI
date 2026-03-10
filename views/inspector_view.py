import streamlit as st
import pandas as pd
from services.blockchain import record_to_blockchain
from components.charts import draw_task_map

def render_inspector_view():
    st.markdown("### 🛡️ 基层巡检·实时作战指挥端")
    tk1, tk2, tk3 = st.columns(3)
    pending = [t for t in st.session_state.task_list if t['status'] == '待核实']
    tk1.metric("待处理工单", len(pending), delta="急需响应" if pending else "暂无")
    tk2.metric("今日办结率", "100%")
    tk3.metric("个人治理积分", "1,240", "+50")

    st.markdown("---")
    t_left, t_right = st.columns([1.5, 1])
    with t_left:
        st.markdown("#### 📋 实时任务队列")
        if not st.session_state.task_list:
            st.info("🍵 流域运行平稳，暂无突发任务。")
        else:
            for idx, item in enumerate(st.session_state.task_list):
                with st.container(border=True):
                    st.write(f"**工单 #{idx + 1}** | {item['time']} | 状态：<span style='color:red;'>{item['status']}</span>", unsafe_allow_html=True)
                    st.write(f"📍 位置：{item.get('address', '浙江省杭州市建德市新安江街道')}  \n🧭 坐标：[经度 {item['lon']:.4f}, 纬度 {item['lat']:.4f}]  \n📝 描述：{item['desc']}")
                    if item['status'] == '待核实':
                        if st.button(f"立即前往处置 #{idx}", type="primary"):
                            item['status'] = '已处理'
                            record_to_blockchain("基层巡检员", f"完结环保工单 #{idx + 1}", f"处置地点:{item['loc']}")
                            st.rerun()
    with t_right:
        st.markdown("#### 📍 突发事件分布")
        if st.session_state.task_list:
            st.plotly_chart(draw_task_map(pd.DataFrame(st.session_state.task_list)), use_container_width=True)