import streamlit as st
import time
import numpy as np
import pandas as pd
from services.blockchain import record_to_blockchain

def render_public_view(geo_df):
    st.markdown("### 🏆 绿水青山·全民参与激励大屏")
    pk1, pk2, pk3, pk4 = st.columns(4)
    pk1.metric("累计参与人次", "12,854", "+142")
    pk2.metric("已发放积分奖励", "64.2万", "+50")
    pk3.metric("有效隐患识别", "8,102件", "98%")
    pk4.metric("积分转化价值", "¥12.5万", "生态分红")

    st.markdown("---")
    p_left, p_right = st.columns([1, 1])
    with p_left:
        with st.container(border=True):
            st.markdown("#### 📸 随手拍异常上报")
            pub_loc = st.selectbox("选择上报点", geo_df['station'])
            pub_desc = st.text_area("描述现场情况", placeholder="如：河面有异味或大面积漂浮物...")
            st.file_uploader("上传照片证据", type=['jpg', 'png'])
            if st.button("🚀 提交研判并获取积分", use_container_width=True):
                st.balloons()
                target_station = geo_df[geo_df['station'] == pub_loc].iloc[0]
                st.session_state.task_list.append({
                    "time": time.strftime("%H:%M"), "loc": pub_loc, "desc": pub_desc, "status": "待核实",
                    "user": "市民" + str(np.random.randint(100, 999)), "lat": target_station['lat'], "lon": target_station['lon']
                })
                tx = record_to_blockchain("社会公众(移动端)", "上传水质污染证据", f"地点:{pub_loc}, 描述:{pub_desc}")
                st.success("✅ 上报成功！获得奖励：50 绿币。")
                st.info(f"🔗 证据已上链存证 | 交易哈希: {tx}")

    with p_right:
        with st.container(border=True):
            st.markdown("#### 🎁 绿币商城：生态红利兑换")
            m1, m2 = st.columns(2)
            with m1:
                st.button("🎟️ 水费阶梯优惠券 (500积分)", use_container_width=True)
                st.button("🚌 公交绿色出行卡 (800积分)", use_container_width=True)
            with m2:
                st.button("🛍️ 生态农产品抵用券 (300积分)", use_container_width=True)
                st.button("💧 净水滤芯更换服务 (1200积分)", use_container_width=True)
            st.line_chart(pd.DataFrame({"本周积分活跃": [120, 150, 132, 180, 210]}), height=150)