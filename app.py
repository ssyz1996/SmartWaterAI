# import streamlit as st
# import pandas as pd
# import numpy as np
# import time
# import pydeck as pdk
# import plotly.graph_objects as go
# from services.ai_core import WaterQualityMLPredictor
# from openai import OpenAI
# import hashlib
# import json
#
# # --- 新增：区块链存证引擎 ---
# if 'blockchain_logs' not in st.session_state:
#     st.session_state.blockchain_logs = []
#
#
# def record_to_blockchain(operator, action, details):
#     """极简数据锚定上链：将关键操作生成哈希，形成不可篡改的凭证"""
#     timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#     # 1. 将操作数据打包
#     raw_data = json.dumps({
#         "op": operator, "act": action, "desc": details, "ts": timestamp
#     }, ensure_ascii=False)
#
#     # 2. 生成 SHA-256 数字指纹模拟链上交易哈希 (TxHash)
#     tx_hash = "0x" + hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
#
#     # 3. 记录到前端日志中 (已融合代码2的desc字段)
#     log_entry = {
#         "time": timestamp,
#         "operator": operator,
#         "action": action,
#         "desc": details,
#         "tx_hash": tx_hash[:24] + "..."  # 截断展示
#     }
#     st.session_state.blockchain_logs.insert(0, log_entry)
#     return tx_hash
#
#
# # ------------------------------
# # --- 1. 页面配置 ---
# st.set_page_config(page_title="浙江省流域数字大屏", layout="wide", initial_sidebar_state="expanded")
#
# # 初始化全局变量
# if 'task_list' not in st.session_state:
#     st.session_state.task_list = []
# if 'god_mode' not in st.session_state:
#     st.session_state['god_mode'] = False
#
# # ========================================================
# # 🎨 UI 美化：高对比度商务版 (亮色地图方案)
# # ========================================================
# st.markdown("""
#     <style>
#     header {visibility: hidden;} footer {visibility: hidden;}
#     .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important; }
#     .block-container { padding-top: 0rem !important; max-width: 98% !important; }
#     .datav-header {
#         text-align: center; padding: 20px 0;
#         background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #1e3a8a 100%);
#         border-bottom: 3px solid #60a5fa; box-shadow: 0 4px 15px rgba(30, 58, 138, 0.4);
#         margin-top: -45px; margin-bottom: 25px;
#     }
#     .datav-title { color: #FFFFFF !important; font-size: 42px !important; font-weight: 900 !important; letter-spacing: 8px !important; }
#     [data-testid="stVerticalBlockBorderWrapper"] {
#         border: 1px solid rgba(59, 130, 246, 0.3) !important; border-radius: 8px !important;
#         background: rgba(255, 255, 255, 0.85) !important; box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1) !important;
#         padding: 15px !important; backdrop-filter: blur(4px);
#     }
#     div[data-testid="stMetricValue"] { font-size: 3rem !important; font-weight: 900 !important; color: #1e3a8a !important; font-family: 'Impact', sans-serif !important; }
#     h4 { color: #1e40af !important; border-left: 5px solid #3b82f6; padding-left: 12px; margin-bottom: 15px !important; }
#     .stMarkdown p, .stCaption, label { color: #1e293b !important; font-weight: 600 !important; font-size: 1.1rem !important; }
#     </style>
# """, unsafe_allow_html=True)
#
#
# # ========================================================
# # 数据处理逻辑
# # ========================================================
# # @st.cache_data
# # def load_timeseries_data(god_mode):
# #     dates = pd.date_range(end=pd.Timestamp.today(), periods=60)
# #     x = np.linspace(0, 15, 60)
# #
# #     df = pd.DataFrame({
# #         'Date': dates,
# #         '酸碱': 7.2 + np.sin(x) * 0.3 + np.random.normal(0, 0.08, 60),
# #         '溶解氧': 6.5 + np.cos(x) * 0.5 + np.random.normal(0, 0.15, 60),
# #         '氨氮': 0.45 + np.sin(x * 1.5) * 0.1 + np.random.normal(0, 0.05, 60),
# #         '总磷': 0.12 + np.cos(x * 1.2) * 0.03 + np.random.normal(0, 0.01, 60),
# #         '浊度': 3.5 + np.sin(x * 0.8) * 0.5 + np.random.normal(0, 0.2, 60)
# #     })
# #
# #     if god_mode:
# #         df.loc[57:59, '酸碱'] = [8.1, 8.8, 9.6]
# #         df.loc[57:59, '溶解氧'] = [5.0, 4.2, 3.1]
# #         df.loc[57:59, '氨氮'] = [0.8, 1.2, 1.8]
# #         df.loc[57:59, '总磷'] = [0.3, 0.5, 0.8]
# #         df.loc[57:59, '浊度'] = [8.0, 12.5, 18.2]
# #     return df
# #
# #
# # @st.cache_data
# # def load_geo_data(god_mode):
# #     ph_levels, colors, elevations = [7.1, 7.2, 6.9, 7.3, 7.5, 7.2, 6.8], [[30, 64, 175, 220] for _ in range(7)], [15000,
# #                                                                                                                   35000,
# #                                                                                                                   12000,
# #                                                                                                                   18000,
# #                                                                                                                   20000,
# #                                                                                                                   14000,
# #                                                                                                                   11000]
# #     if god_mode:
# #         ph_levels[1], colors[1], elevations[1] = 9.6, [185, 28, 28, 255], 90000
# #     return pd.DataFrame(
# #         {"station": ["杭州-新安江", "宁波-姚江", "温州-飞云江", "绍兴-曹娥江", "金华-婺江", "衢州-衢江", "丽水-瓯江"],
# #          "lat": [29.6, 29.87, 27.99, 30.0, 29.08, 28.97, 28.45],
# #          "lon": [119.2, 121.54, 120.69, 120.58, 119.64, 118.86, 119.92], "ph_level": ph_levels, "color": colors,
# #          "elevation": elevations})
#
#
# df = load_timeseries_data(st.session_state['god_mode'])
# geo_df = load_geo_data(st.session_state['god_mode'])
#
# # --- 顶部标题 ---
# st.markdown("<div class='datav-header'><h1 class='datav-title'>全 民 智 水 · 多 模 态 AI 治 水 终 端</h1></div>",
#             unsafe_allow_html=True)
#
#
# # *************************** 实操环节 - 周恬恬 - 大模型工程师****************************************************
# def generate_gov_report(vision_res, xai_df, target_val):
#     """多智能体信息融合，生成政务公文"""
#     top_reason = xai_df.iloc[-1]['污染归因要素']
#     prompt = f"""
#     请作为省水利厅的高级文秘，撰写一份《微流域水质突发恶化情况专报》。
#     输入素材：
#     1. 前端传感器：溶解氧突降至 {target_val}mg/L
#     2. 群众多模态举报：{vision_res.get('pollution_type', '未知')} (危险指数:{vision_res.get('severity_score')})
#     3. AI 算法 XAI 归因：主要致因是【{top_reason}】
#
#     要求：符合政务公文格式，包含【事件概述】【AI溯源分析】【应急处置建议】，字数300字左右。
#     """
#     client = OpenAI(
#         api_key="sk-51004d500a0146c0acfd2764b25d7f65",
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
#     )
#     response = client.chat.completions.create(
#         model="qwen-plus",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content
#
#
#
# # ========================================================
# # 侧边栏：核心融合控制区
# # ========================================================
# with st.sidebar:
#     digital_human_html = """<style>
# .ai-box { background: linear-gradient(180deg, #020617 0%, #0f172a 100%); border-radius: 10px; padding: 12px 10px; text-align: center; border: 1px solid #1d4ed8; box-shadow: 0 0 20px rgba(59,130,246,0.2) inset; height: 310px; position: relative; overflow: hidden; margin-bottom: 15px; }
# .laser-scan { position: absolute; left: 0; right: 0; height: 2px; background: #3b82f6; box-shadow: 0 0 15px #60a5fa; animation: scan 3s linear infinite; opacity: 0.7; }
# @keyframes scan { 0%{top:-10px;} 100%{top:100%;} }
# .hud-container { position: relative; width: 90px; height: 90px; margin: 15px auto; }
# .ring-1 { position: absolute; inset: 0; border: 2px dashed #3b82f6; border-radius: 50%; animation: spin 8s linear infinite; }
# .ring-2 { position: absolute; inset: 10px; border: 2px solid transparent; border-top: 2px solid #10b981; border-right: 2px solid #10b981; border-radius: 50%; animation: spin-rev 3s linear infinite; }
# .core-emoji { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 38px; animation: pulse-glow 2s infinite alternate; }
# @keyframes spin { 100% { transform: rotate(360deg); } }
# @keyframes spin-rev { 100% { transform: rotate(-360deg); } }
# @keyframes pulse-glow { 0% { filter: drop-shadow(0 0 5px #60a5fa); } 100% { filter: drop-shadow(0 0 15px #3b82f6); transform: scale(1.05); } }
# .status-badge { background: rgba(16,185,129,0.15); border: 1px solid #10b981; color: #10b981; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-bottom: 10px; display: inline-block; letter-spacing: 1px; }
# .ai-text { color: #cbd5e1; font-size: 11px; text-align: left; line-height: 1.5; background: rgba(0,0,0,0.5); padding: 8px; border-radius: 8px; border-left: 3px solid #60a5fa; margin-top: 5px;}
# </style>
# <div class="ai-box">
# <div class="laser-scan"></div>
# <div style="color: #94a3b8; font-size: 12px; font-weight: bold; letter-spacing: 2px;">智能水宝AI助手</div>
# <div class="hud-container">
# <div class="ring-1"></div>
# <div class="ring-2"></div>
# <div class="core-emoji">🤖</div>
# </div>
# <div class="status-badge">● 智能体引擎在线</div>
# <div class="ai-text">
# <span style="color: #60a5fa; font-weight: bold;">▶ 实时状态:</span><br>
# 正在执行多模态视觉感知<br>
# 全域水利网络已接管。
# </div>
# </div>"""
#     st.markdown(digital_human_html, unsafe_allow_html=True)
#     st.markdown("### ⚙️ 业务终端切换")
#     user_role = st.selectbox("👤 切换操作视角", [
#         "👑 管理员：决策指挥舱",
#         "👨‍ 巡检员：执行作战端",
#         "📢 社会公众：参与激励端"
#     ])
#     target_obj = st.selectbox("🎯 指标切换", ["酸碱", "溶解氧", "氨氮", "总磷", "浊度"])
#     ml_algorithm = st.radio("🧠 预测模型", [
#         "RF (随机森林)",
#         "GBDT (梯度提升树)",
#         "DT (决策树)",
#         "SVR (支持向量机)",
#         "MLP (神经网络)",
#         "KNN (K近邻)"
#     ])
#     future_days = st.slider("📅 推演天数", 3, 14, 7)
#     start_btn = st.button("🚀 启动全域 AI 推演", type="primary", use_container_width=True)
#
#     # ==========================================
#     # 🌟 核心业务闭环：融合自代码2的AI报警与联动锁死功能
#     # ==========================================
#     if st.button("🚨 模拟突发污染 (触发AI联动)", use_container_width=True):
#         st.session_state['god_mode'] = True
#         st.session_state.pop('future_vals', None)
#
#         # 1. 传感器发现异常上链
#         record_to_blockchain("物联网传感器 (Z2节点)", "自动上报异常读数", "预警：监测到下游水质严重恶化，指标突破红线")
#
#         # 制造极其短暂的时间差，让区块链记录有先后顺序的美感
#         time.sleep(0.05)
#
#         # 2. AI 决策并下发硬件控制指令上链
#         record_to_blockchain("AI 智能决策中枢", "下发物理阀门锁死指令",
#                              "决策：接管底层硬件，物理切断 Z2 闸门(开度降至0%)以阻断污染源")
#         st.rerun()
#
#     if st.button("🔄 解除预警与锁定", use_container_width=True):
#         st.session_state['god_mode'] = False
#         st.session_state.pop('future_vals', None)
#         record_to_blockchain("管理员(指挥舱)", "人工解除警戒状态", "恢复全域水网常态化循环调度")
#         st.rerun()
#
#     if st.button("🚨 多模态AI研判", use_container_width=True):
#         st.session_state['citizen_report'] = True
#
# # ========================================================
# # 视角一：公众视角 - 绿水青山激励舱 (新增商城)
# # ========================================================
# if user_role == "📢 社会公众：参与激励端":
#     st.markdown("### 🏆 绿水青山·全民参与激励大屏")
#     pk1, pk2, pk3, pk4 = st.columns(4)
#     pk1.metric("累计参与人次", "12,854", "+142")
#     pk2.metric("已发放积分奖励", "64.2万", "+50")
#     pk3.metric("有效隐患识别", "8,102件", "98%")
#     pk4.metric("积分转化价值", "¥12.5万", "生态分红")
#
#     st.markdown("---")
#     p_left, p_right = st.columns([1, 1])
#     with p_left:
#         with st.container(border=True):
#             st.markdown("#### 📸 随手拍异常上报")
#             pub_loc = st.selectbox("选择上报点", geo_df['station'])
#             pub_desc = st.text_area("描述现场情况", placeholder="如：河面有异味或大面积漂浮物...")
#             st.file_uploader("上传照片证据", type=['jpg', 'png'])
#             if st.button("🚀 提交研判并获取积分", use_container_width=True):
#                 st.balloons()
#                 target_station = geo_df[geo_df['station'] == pub_loc].iloc[0]
#                 st.session_state.task_list.append(
#                     {"time": time.strftime("%H:%M"), "loc": pub_loc, "desc": pub_desc, "status": "待核实",
#                      "user": "市民" + str(np.random.randint(100, 999)), "lat": target_station['lat'],
#                      "lon": target_station['lon']})
#
#                 tx = record_to_blockchain("社会公众(移动端)", "上传水质污染证据", f"地点:{pub_loc}, 描述:{pub_desc}")
#
#                 st.success("✅ 上报成功！获得奖励：50 绿币。")
#                 st.info(f"🔗 证据已上链存证 | 交易哈希: {tx}")
#
#     with p_right:
#         with st.container(border=True):
#             st.markdown("#### 🎁 绿币商城：生态红利兑换")
#             m1, m2 = st.columns(2)
#             with m1:
#                 st.button("🎟️ 水费阶梯优惠券 (500积分)", use_container_width=True)
#                 st.button("🚌 公交绿色出行卡 (800积分)", use_container_width=True)
#             with m2:
#                 st.button("🛍️ 生态农产品抵用券 (300积分)", use_container_width=True)
#                 st.button("💧 净水滤芯更换服务 (1200积分)", use_container_width=True)
#             st.line_chart(pd.DataFrame({"本周积分活跃": [120, 150, 132, 180, 210]}), height=150)
#
#
# # ========================================================
# # 视角二：巡检员视角 - 数字化作战指挥端
# # ========================================================
# elif user_role == "👨‍ 巡检员：执行作战端":
#     st.markdown("### 🛡️ 基层巡检·实时作战指挥端")
#     tk1, tk2, tk3 = st.columns(3)
#     pending = [t for t in st.session_state.task_list if t['status'] == '待核实']
#     tk1.metric("待处理工单", len(pending), delta="急需响应" if pending else "暂无")
#     tk2.metric("今日办结率", "100%")
#     tk3.metric("个人治理积分", "1,240", "+50")
#
#     st.markdown("---")
#     t_left, t_right = st.columns([1.5, 1])
#     with t_left:
#         st.markdown("#### 📋 实时任务队列")
#         if not st.session_state.task_list:
#             st.info("🍵 流域运行平稳，暂无突发任务。")
#         else:
#             for idx, item in enumerate(st.session_state.task_list):
#                 with st.container(border=True):
#                     st.write(
#                         f"**工单 #{idx + 1}** | {item['time']} | 状态：<span style='color:red;'>{item['status']}</span>",
#                         unsafe_allow_html=True)
#                     st.write(f"📍 位置：{item.get('address', '浙江省杭州市建德市新安江街道')}  \n"
#                              f"🧭 坐标：[经度 {item['lon']:.4f}, 纬度 {item['lat']:.4f}]  \n"
#                              f"📝 描述：{item['desc']}")
#                     if item['status'] == '待核实':
#                         if st.button(f"立即前往处置 #{idx}", type="primary"):
#                             item['status'] = '已处理'
#                             record_to_blockchain("基层巡检员", f"完结环保工单 #{idx + 1}", f"处置地点:{item['loc']}")
#                             st.rerun()
#     with t_right:
#         st.markdown("#### 📍 突发事件分布")
#         if st.session_state.task_list:
#             df_tasks = pd.DataFrame(st.session_state.task_list)
#             fig_map = go.Figure(go.Scattermapbox(
#                 lat=df_tasks['lat'],
#                 lon=df_tasks['lon'],
#                 mode='markers',
#                 marker=go.scattermapbox.Marker(size=16, color='#dc2626', opacity=0.9),
#                 text=df_tasks['loc'] + "：" + df_tasks['desc'], hoverinfo='text'
#             ))
#             fig_map.update_layout(
#                 mapbox_style="white-bg",
#                 mapbox_layers=[{
#                     "below": 'traces', "sourcetype": "raster",
#                     "source": [
#                         "https://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7"]
#                 }],
#                 mapbox=dict(center=dict(lat=29.2, lon=120.1), zoom=6.5),
#                 margin=dict(l=0, r=0, t=0, b=0), height=350, paper_bgcolor='rgba(0,0,0,0)'
#             )
#             st.plotly_chart(fig_map, use_container_width=True)
#
#
# # ========================================================
# # 视角三：管理员视角 - 数字化决策大屏
# # ========================================================
# elif user_role == "👑 管理员：决策指挥舱":
#     k1, k2, k3, k4, k5 = st.columns(5)
#     with k1:
#         st.metric("📡 在线设备", "12,402", "100%")
#     with k2:
#         st.metric(f"💧 {target_obj} 极值", f"{df[target_obj].iloc[-1]:.2f}",
#                   "+2.40!" if st.session_state['god_mode'] else "稳定",
#                   delta_color="inverse" if st.session_state['god_mode'] else "normal")
#     with k3:
#         st.metric("🔗 链上存证量", f"{len(st.session_state.blockchain_logs)} 笔",
#                   "不可篡改" if st.session_state.blockchain_logs else "实时监控")
#     with k4:
#         st.metric("🏭 涉水监控", "3,105", "12家异常")
#     with k5:
#         st.metric("🧠 算力状态", "24.5%", "运行健康")
#
#     # ========================================================
#     # 🌟 专属展示：主页区块链核心展示区 (布局重构，新增动态拓扑图)
#     # ========================================================
#     st.markdown("### 🔗 Web3.0 区块链数据信任确权中心")
#
#     st.markdown("""
#     <style>
#     @keyframes pulse-green {
#         0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
#         70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
#         100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
#     }
#     @keyframes scroll-hash {
#         0% { transform: translateY(0); }
#         100% { transform: translateY(-50%); }
#     }
#     @keyframes spin-slow { 100% { transform: rotate(360deg); } }
#     @keyframes spin-rev { 100% { transform: rotate(-360deg); } }
#
#     .bc-card {
#         background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
#         border: 1px solid #cbd5e1;
#         border-radius: 8px;
#         padding: 15px;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.03);
#         position: relative;
#         overflow: hidden;
#         height: 290px;
#     }
#     .hash-bg {
#         position: absolute; right: -10px; top: 0; bottom: 0; width: 140px;
#         font-family: monospace; font-size: 10px; color: rgba(59, 130, 246, 0.06);
#         line-height: 1.2; word-break: break-all; z-index: 0;
#         animation: scroll-hash 15s linear infinite;
#     }
#     </style>
#     """, unsafe_allow_html=True)
#
#     # 💡 核心修改点：将比例从 [1.2, 2.5] 改为 3列 [1.1, 1.8, 1.0]，压缩账本宽度，给右侧拓扑图腾出空间
#     bc_col1, bc_col2, bc_col3 = st.columns([1.1, 1.7, 1.1])
#
#     fake_hashes = "<br>".join([hashlib.sha256(str(i).encode()).hexdigest()[:24] for i in range(40)])
#
#     # 左侧：底层链状态
#     with bc_col1:
#         current_blocks = 12045 + len(st.session_state.blockchain_logs)
#         new_blocks = len(st.session_state.blockchain_logs)
#
#         node_html = f"""
# <div class="bc-card">
# <div class="hash-bg">{fake_hashes}{fake_hashes}</div>
# <div style="position: relative; z-index: 1;">
# <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px;">
# <span style="font-weight:900; color:#1e3a8a; font-size:16px;">FISCO BCOS 底层链</span>
# <div style="display:flex; align-items:center; gap:6px; background:#d1fae5; color:#047857; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
# <div style="width:8px; height:8px; background:#10b981; border-radius:50%; animation: pulse-green 2s infinite;"></div> 共识中
# </div>
# </div>
# <div style="margin-bottom: 20px;">
# <div style="color: #64748b; font-size: 12px; font-weight: bold; margin-bottom: 2px;">📦 实时区块高度 (Block Height)</div>
# <div style="font-family: 'Impact', sans-serif; font-size: 34px; color: #0f172a; text-shadow: 2px 2px 0px #e2e8f0;">#{current_blocks}</div>
# <div style="color: #3b82f6; font-size: 11px; font-weight: bold; margin-top: 2px;">↑ 相比系统启动新增 <span style="color:#ef4444;">{new_blocks}</span> 个确权区块</div>
# </div>
# <div>
# <div style="color: #64748b; font-size: 12px; font-weight: bold; margin-bottom: 6px;">📜 核心治理智能合约</div>
# <div style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 12px; color: #1e293b; display: flex; justify-content: space-between; align-items: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
# <span>0x7a2...3f9</span>
# <span style="color:#10b981; font-size: 12px;">✓ 活跃</span>
# </div>
# </div>
# </div>
# </div>
# """
#         st.markdown(node_html, unsafe_allow_html=True)
#
#     # 中间：缩窄后的分布式账本
#     with bc_col2:
#         if not st.session_state.blockchain_logs:
#             empty_html = """
# <div class="bc-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
# <div style="position: relative; width: 80px; height: 80px; margin-bottom: 20px;">
# <div style="position: absolute; inset: 0; border: 3px dashed #94a3b8; border-radius: 50%; animation: spin-slow 8s linear infinite;"></div>
# <div style="position: absolute; inset: 12px; border: 3px solid transparent; border-top: 3px solid #3b82f6; border-right: 3px solid #3b82f6; border-radius: 50%; animation: spin-rev 3s linear infinite;"></div>
# <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 28px;">📡</div>
# </div>
# <div style="color: #1e293b; font-size: 18px; font-weight: 900; margin-bottom: 8px;">全网区块节点防篡改监听中...</div>
# <div style="color: #64748b; font-size: 12px; line-height: 1.6;">
# 智能合约处于挂起状态。当系统触发 <span style="color:#ef4444; font-weight:bold;">[模拟突发污染]</span> 或公众提交举报时，<br>
# 底层的哈希存证机制将自动触发并写入下一个安全区块。
# </div>
# </div>
# """
#             st.markdown(empty_html, unsafe_allow_html=True)
#         else:
#             blocks_html = ""
#             for i, log in enumerate(st.session_state.blockchain_logs[:3]):
#                 is_latest = (i == 0)
#                 border_style = "2px solid #3b82f6" if is_latest else "1px solid #cbd5e1"
#                 bg_color = "#eff6ff" if is_latest else "#ffffff"
#                 badge = "<span style='background:#3b82f6; color:white; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:bold; position:absolute; top:-8px; right:15px;'>🌟 最新生成区块</span>" if is_latest else ""
#
#                 blocks_html += f"""
# <div style="background: {bg_color}; border: {border_style}; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
# {badge}
# <div style="display:flex; justify-content:space-between; font-size:12px; color:#64748b; margin-bottom:8px;">
# <span style="font-family:monospace;">{log['time']}</span>
# <span style="font-weight:bold; color:#1e293b;">{log['operator']}</span>
# </div>
# <div style="font-weight:bold; color:#0f172a; font-size:13px; margin-bottom:6px;">
# <span style="color:#ef4444; background:#fee2e2; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:5px;">核心指令</span> {log['action']}
# </div>
# <div style="color:#475569; font-size:11px; margin-bottom:6px; line-height:1.4;">
# <span style="font-weight:bold;">执行详情：</span>{log.get('desc', '已在全网广播')}
# </div>
# <div style="background:#f1f5f9; padding:6px 8px; border-radius:6px; font-family:monospace; font-size:11px; color:#64748b; display:flex; justify-content:space-between; align-items:center;">
# <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:75%;"><span style="color:#3b82f6; font-weight:bold;">TxHash:</span> {log['tx_hash']}</span>
# <span style="color:#10b981; font-weight:900;">🔗 已确权</span>
# </div>
# </div>
# """
#                 if i < min(len(st.session_state.blockchain_logs), 3) - 1:
#                     blocks_html += """<div style="text-align:center; color:#94a3b8; font-size:14px; margin-bottom:6px; line-height:1;">⬇</div>"""
#
#             log_html = f"""
# <div class="bc-card" style="overflow-y: auto;">
# <div style="position: sticky; top: -15px; background: rgba(255,255,255,0.95); backdrop-filter: blur(5px); padding: 0 0 10px 0; margin-top: -5px; z-index: 10; border-bottom: 1px dashed #e2e8f0; margin-bottom: 12px;">
# <span style="font-weight:900; color:#1e3a8a; font-size:16px;">⛓️ 实时分布式账本 (Ledger)</span>
# </div>
# {blocks_html}
# </div>
# """
#             st.markdown(log_html, unsafe_allow_html=True)
#
#         # 💡 新增右侧：高科技的纯 CSS 动态共识节点拓扑网络
#         with bc_col3:
#             # ⚠️ 注意：下面的 HTML 字符串必须顶格写（没有缩进），否则会被 Markdown 当成代码块！
#             topology_html = """<div class="bc-card" style="display: flex; flex-direction: column;">
# <div style="font-weight:900; color:#1e3a8a; font-size:15px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 8px; margin-bottom: 15px; z-index: 2;">
# 🌐 联盟链节点动态拓扑
# </div>
#
# <div style="flex: 1; position: relative; display: flex; justify-content: center; align-items: center; min-height: 160px;">
# <style>
# @keyframes pulse-core { 0% { box-shadow: 0 0 0 0 rgba(59,130,246,0.6); } 70% { box-shadow: 0 0 0 10px rgba(59,130,246,0); } 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0); } }
# @keyframes orbit1 { 0% { transform: rotate(0deg) translateX(65px) rotate(0deg); } 100% { transform: rotate(360deg) translateX(65px) rotate(-360deg); } }
# @keyframes orbit2 { 0% { transform: rotate(90deg) translateX(65px) rotate(-90deg); } 100% { transform: rotate(450deg) translateX(65px) rotate(-450deg); } }
# @keyframes orbit3 { 0% { transform: rotate(180deg) translateX(65px) rotate(-180deg); } 100% { transform: rotate(540deg) translateX(65px) rotate(-540deg); } }
# @keyframes orbit4 { 0% { transform: rotate(270deg) translateX(65px) rotate(-270deg); } 100% { transform: rotate(630deg) translateX(65px) rotate(-630deg); } }
# .orbit-node { position: absolute; width: 44px; height: 44px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 10px; font-weight: bold; color: white; z-index: 5; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 2px solid #ffffff;}
# </style>
#
# <div style="position: absolute; width: 56px; height: 56px; background: linear-gradient(135deg, #1e3a8a, #3b82f6); border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; font-weight: 900; font-size: 11px; z-index: 10; animation: pulse-core 2s infinite; border: 2px solid #ffffff; line-height: 1.2;">
# <span>核心</span><span>合约</span>
# </div>
#
# <div style="position: absolute; width: 130px; height: 130px; border: 1px dashed #94a3b8; border-radius: 50%; z-index: 1; animation: spin-slow 15s linear infinite;"></div>
# <div style="position: absolute; width: 85px; height: 85px; border: 1px solid #e2e8f0; border-radius: 50%; z-index: 1;"></div>
#
# <div class="orbit-node" style="background: linear-gradient(135deg, #059669, #10b981); animation: orbit1 12s linear infinite;">水利局</div>
# <div class="orbit-node" style="background: linear-gradient(135deg, #dc2626, #ef4444); animation: orbit2 12s linear infinite;">AI中枢</div>
# <div class="orbit-node" style="background: linear-gradient(135deg, #d97706, #f59e0b); animation: orbit3 12s linear infinite;">环保局</div>
# <div class="orbit-node" style="background: linear-gradient(135deg, #7c3aed, #8b5cf6); animation: orbit4 12s linear infinite;">公众端</div>
# </div>
#
# <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 11px; color: #475569; margin-top: 15px; border: 1px solid #cbd5e1;">
# <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
# <span>⚡ 全网算力状态</span><span style="font-weight: bold; color: #10b981;">12.4 TH/s (健康)</span>
# </div>
# <div style="display: flex; justify-content: space-between;">
# <span>⏱️ 平均共识延迟</span><span style="font-weight: bold; color: #3b82f6;">12 ms</span>
# </div>
# </div>
# </div>"""
#             st.markdown(topology_html, unsafe_allow_html=True)
#
#     st.markdown("---")
#
#     # ================= 第一排：演化图与仪表盘 =================
#     col_top_left, col_top_right = st.columns([1.5, 1])
#
#     with col_top_left:
#         with st.container(border=True):
#             st.markdown("#### 📈 多维特征动态演化")
#             metrics_list = ["酸碱", "溶解氧", "氨氮", "总磷", "浊度"]
#             tabs = st.tabs(metrics_list)
#             for i, tab in enumerate(tabs):
#                 with tab:
#                     curr_metric = metrics_list[i]
#                     fig_evo = go.Figure()
#                     fig_evo.add_trace(go.Scatter(
#                         x=df['Date'], y=df[curr_metric], fill='tozeroy', mode='lines',
#                         line=dict(color='#3b82f6', width=2), fillcolor='rgba(59, 130, 246, 0.2)'
#                     ))
#                     fig_evo.update_layout(
#                         margin=dict(l=10, r=10, t=10, b=10), height=220,
#                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#                         xaxis=dict(showgrid=False, tickformat="%m月%d日", hoverformat="%Y年%m月%d日"),
#                         yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
#                     )
#                     st.plotly_chart(fig_evo, use_container_width=True, key=f"evo_{curr_metric}")
#
#     with col_top_right:
#         with st.container(border=True):
#             st.markdown("#### 🌊 核心协同设备参数")
#
#             # ==========================================
#             # 1. 压缩上方的仪表盘尺寸
#             # ==========================================
#             twin_gate_open_pct = 0 if st.session_state.get('god_mode', False) else 85
#             twin_pump_load = 92 if st.session_state.get('god_mode', False) else 68
#
#             title_font = {'size': 11, 'color': '#1e293b'}  # 缩小标题
#             num_font = {'size': 16, 'color': '#1e3a8a'}  # 缩小数字
#             fig_gauge = go.Figure()
#
#             fig_gauge.add_trace(
#                 go.Indicator(mode="gauge+number", value=82,
#                              title={'text': "土壤饱和度(%)", 'font': title_font}, number={'font': num_font},
#                              gauge={'axis': {'range': [0, 100], 'showticklabels': False}, 'bar': {'color': "#3b82f6"}},
#                              domain={'x': [0, 0.45], 'y': [0.55, 1]}))
#
#             fig_gauge.add_trace(
#                 go.Indicator(mode="gauge+number", value=twin_gate_open_pct,
#                              title={'text': "水闸开启度(%)", 'font': title_font}, number={'font': num_font},
#                              gauge={'axis': {'range': [0, 100], 'showticklabels': False},
#                                     'bar': {'color': "#10b981" if twin_gate_open_pct > 0 else "#ef4444"}},
#                              domain={'x': [0.55, 1], 'y': [0.55, 1]}))
#
#             fig_gauge.add_trace(
#                 go.Indicator(mode="gauge+number", value=twin_pump_load,
#                              title={'text': "泵站负荷(%)", 'font': title_font}, number={'font': num_font},
#                              gauge={'axis': {'range': [0, 100], 'showticklabels': False},
#                                     'bar': {'color': "#f59e0b" if twin_pump_load < 90 else "#ef4444"}},
#                              domain={'x': [0, 0.45], 'y': [0, 0.4]}))
#
#             fig_gauge.add_trace(
#                 go.Indicator(mode="gauge+number", value=45,
#                              title={'text': "管网压力(kPa)", 'font': title_font}, number={'font': num_font},
#                              gauge={'axis': {'range': [0, 100], 'showticklabels': False}, 'bar': {'color': "#8b5cf6"}},
#                              domain={'x': [0.55, 1], 'y': [0, 0.4]}))
#
#             # 高度从 180 压缩至 120，为下方阀门让出巨大空间
#             fig_gauge.update_layout(height=120, margin=dict(l=10, r=10, t=25, b=0), paper_bgcolor='rgba(0,0,0,0)')
#             st.plotly_chart(fig_gauge, use_container_width=True)
#
#             # ==========================================
#             # 2. 放大并差异化阀门孪生体渲染
#             # ==========================================
#             is_emergency = st.session_state.get('god_mode', False)
#
#             # 🌟 神级细节：给三个设备配上不同的材质、外壳色、水流色
#             gate_nodes = [
#                 {"name": "杭州新安江·Z1", "n_open": 85, "e_open": 30, "n_flow": "125.4", "e_flow": "42.1",
#                  "casing": "#e2e8f0", "border": "#64748b", "water": "linear-gradient(180deg, #60a5fa 0%, #1e3a8a 100%)",
#                  "gate": "linear-gradient(90deg, #94a3b8 0%, #cbd5e1 50%, #94a3b8 100%)", "gate_border": "#f59e0b"},
#                 # 银闸+标准蓝水
#                 {"name": "宁波姚江·Z2", "n_open": 80, "e_open": 0, "n_flow": "98.2", "e_flow": "0.0",
#                  "casing": "#f8fafc", "border": "#475569", "water": "linear-gradient(180deg, #34d399 0%, #047857 100%)",
#                  "gate": "linear-gradient(90deg, #fbbf24 0%, #fcd34d 50%, #fbbf24 100%)", "gate_border": "#d97706"},
#                 # 黄铜闸+碧绿水
#                 {"name": "温州飞云江·Z3", "n_open": 90, "e_open": 20, "n_flow": "156.0", "e_flow": "28.5",
#                  "casing": "#cbd5e1", "border": "#334155", "water": "linear-gradient(180deg, #38bdf8 0%, #0c4a6e 100%)",
#                  "gate": "linear-gradient(90deg, #a1a1aa 0%, #e4e4e7 50%, #a1a1aa 100%)", "gate_border": "#52525b"}
#                 # 深钛闸+深青水
#             ]
#
#             gates_html_content = ""
#             for i, node in enumerate(gate_nodes):
#                 current_open = node['e_open'] if is_emergency else node['n_open']
#                 current_flow = node['e_flow'] if is_emergency else node['n_flow']
#
#                 if current_open == 0:
#                     status_color, status_text, gate_top = "#ef4444", "🚨 紧急锁死", "0%"
#                 elif current_open < 50:
#                     status_color, status_text, gate_top = "#f59e0b", "🟡 压减泄洪", f"-{current_open}%"
#                 else:
#                     status_color, status_text, gate_top = "#10b981", "🟢 自动调度", f"-{current_open}%"
#
#                 # 宽高从 45x60 放大到 60x85，动态提取配置中的颜色变量
#                 gates_html_content += f"""
#             <div style="flex: 1; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.08); margin: 0 4px; display: flex; flex-direction: column;">
#             <div style="font-size: 11px; font-weight: 800; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px; text-align: center;">{node['name']}</div>
#             <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
#
#             <div style="width: 60px; height: 85px; background: {node['casing']}; position: relative; overflow: hidden; border-left: 6px solid {node['border']}; border-right: 6px solid {node['border']}; border-top: 6px solid #1e293b; border-radius: 3px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
#             <div style="position: absolute; bottom: 0; width: 100%; height: 55%; background: {node['water']}; z-index: 1;"></div>
#             <div style="position: absolute; top: {gate_top}; left: 0; width: 100%; height: 100%; background: {node['gate']}; border-bottom: 4px solid {node['gate_border']}; z-index: 2; transition: top 1.2s cubic-bezier(0.4, 0, 0.2, 1); display: flex; flex-direction: column; justify-content: space-evenly; align-items: center;">
#             <div style="width: 100%; height: 2px; background: rgba(0,0,0,0.2); box-shadow: 0 1px 1px rgba(255,255,255,0.4);"></div>
#             <div style="width: 100%; height: 2px; background: rgba(0,0,0,0.2); box-shadow: 0 1px 1px rgba(255,255,255,0.4);"></div>
#             <div style="width: 100%; height: 2px; background: rgba(0,0,0,0.2); box-shadow: 0 1px 1px rgba(255,255,255,0.4);"></div>
#             <div style="width: 100%; height: 2px; background: rgba(0,0,0,0.2); box-shadow: 0 1px 1px rgba(255,255,255,0.4);"></div>
#             </div>
#             </div>
#
#             <div style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #475569; line-height: 1.6;">
#             <div style="color: {status_color}; font-weight: 900; font-family: sans-serif; font-size: 13px; margin-bottom: 4px;">{status_text}</div>
#             <div>开度:<span style="color: #0284c7; font-weight: 900; font-size: 14px; margin-left: 2px;">{current_open}%</span></div>
#             <div>流量:<span style="color: #334155; font-weight: bold; margin-left: 2px;">{current_flow}</span></div>
#             <div style="color: #94a3b8; font-size: 10px; margin-top: 4px;">Temp: 4{i}.{i * 2}℃</div>
#             </div>
#             </div>
#             </div>
#             """
#
#             twin_html = f"""
#             <div style="padding: 12px 8px; background: #f8fafc; border-radius: 8px; border: 1px solid #cbd5e1; margin-top:5px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
#             <div style="color: #0f172a; font-size: 14px; font-weight: 900; margin-bottom: 12px; margin-left: 5px; border-left: 4px solid #3b82f6; padding-left: 8px;">🏗️ 全流域水利枢纽孪生控制阵列</div>
#             <div style="display: flex; justify-content: space-between;">
#             {gates_html_content}
#             </div>
#             </div>
#             """
#             st.markdown(twin_html, unsafe_allow_html=True)
#
#     # ================= 第二排：雷达图、日志与地图 =================
#     col_bot_left, col_bot_right = st.columns([1, 2.2])
#
#     with col_bot_left:
#         with st.container(border=True):
#             st.markdown("#### 🎯 水质生态雷达")
#             radar_fig = go.Figure()
#             radar_fig.add_trace(
#                 go.Scatterpolar(r=[7.2, 6.5, 2.5, 3.1, 4.0], theta=['酸碱', '溶解氧', '氨氮', '总磷', '浊度'],
#                                 fill='toself', line_color='#1e3a8a', fillcolor='rgba(30, 64, 175, 0.2)'))
#             radar_fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 15]), bgcolor='rgba(0,0,0,0)'),
#                                     paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#1e3a8a', size=11),
#                                     margin=dict(l=15, r=15, t=15, b=15), height=180, showlegend=False)
#             st.plotly_chart(radar_fig, use_container_width=True)
#
#         with st.container(border=True):
#             st.markdown("#### 📜 系统指令流日志")
#             logs_data = [
#                 "10:42 🟢 [温州飞云江] 泵站P2运行平稳，流量正常",
#                 "10:35 🟡 [杭州新安江] 浊度轻微上升，已开启AI关注",
#                 "10:12 🟢 [绍兴曹娥江] 水闸Z1已执行自动化关闭",
#                 "09:58 🟢 [金华婺江] 溶解氧恢复至正常区间(>5.0)",
#                 "09:30 🔵 [系统内核] XAI周期性特征自适应校准完成",
#                 "09:15 🟢 [宁波姚江] 近岸水位监测点读数正常",
#                 "08:45 🔵 [社会端] 收到 12 条有效公众上报巡检记录"
#             ]
#
#             # 🌟 融合代码2：当预警发生时，写入高度定制的业务联动日志
#             if st.session_state['god_mode']:
#                 logs_data.insert(0, "10:45 🔒 [区块链存证] 智能合约已将本次【AI协同控制命令】永久上链！")
#                 logs_data.insert(1, "10:45 🚨 [硬件接管] 智能体已接管底层 PLC，Z2 主控水闸执行紧急锁死！")
#                 logs_data.insert(2, "10:45 🚨 [污染报警] 物联网节点发现【宁波姚江】数据突变，大模型介入拦截！")
#
#             inner_html = ""
#             for log in logs_data:
#                 # 处理新增的区块链 🔒 标识颜色
#                 color = "#dc2626" if "🚨" in log else (
#                     "#8b5cf6" if "🔒" in log else ("#d97706" if "🟡" in log else "#1e3a8a"))
#                 weight = "bold" if ("🚨" in log or "🔒" in log) else "normal"
#                 inner_html += f"<div style='color:{color}; font-weight:{weight}; border-bottom:1px dashed #cbd5e1; padding-bottom:3px; margin-bottom:3px;'>{log}</div>"
#
#             css_animation = """
#                 <style>
#                 @keyframes scroll-logs { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
#                 .log-box { height: 120px; overflow: hidden; font-family: monospace; font-size: 12px; line-height: 1.4; position: relative; }
#                 .log-content { animation: scroll-logs 12s linear infinite; }
#                 .log-content:hover { animation-play-state: paused; cursor: pointer; }
#                 </style>
#                 """
#             full_html = css_animation + f"<div class='log-box'><div class='log-content'>{inner_html}{inner_html}</div></div>"
#             st.markdown(full_html, unsafe_allow_html=True)
#
#     with col_bot_right:
#         view_state = pdk.ViewState(latitude=29.2, longitude=120.1, zoom=6.2, pitch=45)
#         geojson = pdk.Layer("GeoJsonLayer", data="https://geo.datav.aliyun.com/areas_v3/bound/330000_full.json",
#                             stroked=True, filled=True, get_fill_color=[241, 245, 249], get_line_color=[30, 58, 138],
#                             line_width_min_pixels=2)
#         columns = pdk.Layer('ColumnLayer', data=geo_df, get_position='[lon, lat]', get_elevation='elevation',
#                             elevation_scale=1, radius=9000, get_fill_color='color', pickable=True)
#         with st.container(border=True):
#             st.pydeck_chart(pdk.Deck(layers=[geojson, columns], initial_view_state=view_state, map_provider=None,
#                                      tooltip={"text": "{station}\n指标: {ph_level}"}), use_container_width=True)
#     st.markdown("---")
#
#     # ================= 第三排：AI 控制与多模态预警舱 =================
#     anomaly_checker = WaterQualityMLPredictor()
#     is_anomaly, val = anomaly_checker.detect_sudden_anomaly(df, target_obj)
#
#     if is_anomaly and 'report_generated' not in st.session_state:
#         st.session_state['trigger_emergency_report'] = True
#         st.session_state['emergency_val'] = val
#
#     if start_btn:
#         model_key = ml_algorithm.split(" ")[0]
#         predictor = WaterQualityMLPredictor(model_type=model_key)
#         st.session_state.update({
#             'future_vals': predictor.train_and_predict(df, target_col=target_obj, future_steps=future_days),
#             'target_obj': target_obj,
#             'future_days': future_days
#         })
#         if model_key in ['RF', 'GBDT', 'DT']:
#             st.session_state['xai_data'] = predictor.get_xai_feature_importance()
#         elif 'xai_data' in st.session_state:
#             del st.session_state['xai_data']
#
#     if st.session_state.get('citizen_report'):
#         st.markdown("<h3 style='color:#dc2626;'>🚨 多模态 AI 紧急拦截舱</h3>", unsafe_allow_html=True)
#         with st.container(border=True):
#             col1, col2 = st.columns([1, 2])
#             with col1:
#                 st.image("photo/水.jpg", caption="公众随手拍现场照片")
#             with col2:
#                 with st.spinner("AI 视觉大模型正在解析图像..."):
#                     analysis = analyze_citizen_photo("photo/水.jpg")
#                 st.error(f"⚠️ **AI 视觉预警**：检测到 {analysis['pollution_type']}")
#                 st.warning(f"📉 **量化评级**：危险指数 {analysis['severity_score']}/10.0")
#                 st.info(f"💡 **AI 建议**：{analysis['ai_suggestion']}")
#                 if st.button("🚀 采纳 AI 建议，一键派发基层巡检员", type="primary"):
#                     st.session_state.task_list.insert(0, {
#                         "time": "刚刚", "loc": "公众上报隐患点",
#                         "desc": f"【AI协同工单】{analysis['pollution_type']}",
#                         "status": "紧急待办", "user": "多模态智水Agent",
#                         "lat": 29.6001, "lon": 119.2005,
#                         "address": "浙江省杭州市建德市新安江街道"
#                     })
#                     st.toast("✅ 派单成功！已直达巡检员手机终端！")
#                     st.session_state['citizen_report'] = False
#
#     if 'future_vals' in st.session_state:
#         p_col, x_col = st.columns([1.5, 1])
#         with p_col:
#             with st.container(border=True):
#                 st.markdown("#### 🧠 AI 多维时序预测推演")
#                 past_dates = df['Date'].iloc[-14:]
#                 past_vals = df[st.session_state['target_obj']].iloc[-14:]
#                 future_dates = pd.date_range(start=df['Date'].iloc[-1] + pd.Timedelta(days=1),
#                                              periods=len(st.session_state['future_vals']))
#
#                 fig_pred = go.Figure()
#                 fig_pred.add_trace(go.Scatter(x=past_dates, y=past_vals, mode='lines+markers', name='历史真实数据',
#                                               line=dict(color='#3b82f6', width=2)))
#                 pred_x = [past_dates.iloc[-1]] + list(future_dates)
#                 pred_y = [past_vals.iloc[-1]] + st.session_state['future_vals']
#                 fig_pred.add_trace(go.Scatter(x=pred_x, y=pred_y, mode='lines+markers', name='AI推演走势',
#                                               line=dict(color='#ef4444', width=2, dash='dash')))
#                 fig_pred.update_layout(
#                     height=230, margin=dict(l=0, r=0, t=10, b=0),
#                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#                     xaxis=dict(tickformat="%m月%d日", hoverformat="%Y年%m月%d日"),
#                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#                 )
#                 st.plotly_chart(fig_pred, use_container_width=True)
#
#         with x_col:
#             with st.container(border=True):
#                 st.markdown("#### 💡 核心异动溯源归因")
#                 if 'xai_data' in st.session_state:
#                     xai_df = st.session_state['xai_data']
#                     fig_xai = go.Figure(data=[
#                         go.Pie(labels=xai_df['污染归因要素'], values=xai_df['权重贡献度'], hole=.45,
#                                textinfo='label+percent', textposition='outside',
#                                textfont=dict(size=14, color='#1e293b', family="Arial, sans-serif"),
#                                marker=dict(colors=['#ef4444', '#f59e0b', '#10b981', '#3b82f6'],
#                                            line=dict(color='#ffffff', width=2)))
#                     ])
#                     fig_xai.update_layout(height=260, margin=dict(l=40, r=40, t=15, b=40), showlegend=False,
#                                           paper_bgcolor='rgba(0,0,0,0)')
#                     st.plotly_chart(fig_xai, use_container_width=True)
#                 else:
#                     st.info("💡 请在左侧侧边栏切换至树模型 (RF/GBDT/DT) 开启可解释归因分析")
#
#     # ================= 第四排：多智能体助手与专报 =================
#     with st.container(border=True):
#         st.markdown("#### 🤖 水宝智能AI助手 Smart AI Assistant")
#
#         LLM_API_KEY = "sk-51004d500a0146c0acfd2764b25d7f65"
#         LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
#         LLM_MODEL_NAME = "qwen-plus"
#
#         client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
#
#         if "messages" not in st.session_state:
#             st.session_state.messages = []
#
#         for msg in st.session_state.messages:
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])
#
#         prompt = st.chat_input("下达研判指令... (例如：分析当前水质情况，并给出治理建议)")
#         if prompt:
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             with st.chat_message("user"):
#                 st.markdown(prompt)
#
#             latest_ph = df['酸碱'].iloc[-1]
#             latest_do = df['溶解氧'].iloc[-1]
#             latest_nh3n = df['氨氮'].iloc[-1]
#             latest_tp = df['总磷'].iloc[-1]
#             latest_turb = df['浊度'].iloc[-1]
#
#             status_text = "【紧急突发状态：水质严重异常！】" if st.session_state['god_mode'] else "【平稳正常】"
#             tasks_info = "\n".join([f"- 位置:{t['loc']} | 描述:{t['desc']} | 状态:{t['status']}" for t in
#                                     st.session_state.task_list]) if st.session_state.task_list else "暂无公众上报事件"
#
#             system_prompt = f"""
#                     你是一个名为"浙江政务 Data Copilot"的智慧水务数字孪生AI助手。
#                     请严格基于以下【实时监测数据】回答用户的研判指令：
#                     [当前流域整体状态]：{status_text}
#                     [最新实时水质指标]：酸碱度={latest_ph:.2f}, 溶解氧={latest_do:.2f}mg/L, 氨氮={latest_nh3n:.2f}mg/L, 总磷={latest_tp:.2f}mg/L, 浊度={latest_turb:.2f}NTU
#                     [待处理公众上报工单]：
#                     {tasks_info}
#             回答要求：
#             1. 语气必须是专业、严谨的政务决策辅助口吻，排版清晰美观。
#             2. 如果发现水质异常，必须立刻给出应急处置与溯源排查建议。
#             """
#
#             with st.chat_message("assistant"):
#                 message_placeholder = st.empty()
#                 full_response = ""
#                 try:
#                     api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
#                     response = client.chat.completions.create(
#                         model=LLM_MODEL_NAME, messages=api_messages, stream=True,
#                     )
#                     for chunk in response:
#                         if chunk.choices[0].delta.content is not None:
#                             full_response += chunk.choices[0].delta.content
#                             message_placeholder.markdown(full_response + "▌")
#                     message_placeholder.markdown(full_response)
#                 except Exception as e:
#                     full_response = f"⚠️ **系统提示**：连接失败。\n\n*错误：{str(e)}*"
#                     message_placeholder.markdown(full_response)
#
#             st.session_state.messages.append({"role": "assistant", "content": full_response})
#
#     if st.session_state.get('trigger_emergency_report'):
#         st.markdown("---")
#         st.error("系统侦测到严重水质突变，自动研判预警机制已启动！")
#
#         with st.status("多智能体协同正在撰写水质专报...", expanded=True) as status:
#             st.write("1. 调取时序突变检测算法...")
#             st.write("2. 融合多模态视觉溯源...")
#             st.write("3. 提取归因权重分布...")
#
#             if 'gov_report' not in st.session_state:
#                 vision_res = st.session_state.get('vision_res',
#                                                   {'pollution_type': '水面大面积漂浮物', 'severity_score': 8.5})
#                 fallback_xai = pd.DataFrame({"污染归因要素": ["工业偷排或面源污染(兜底推测)"], "权重贡献度": [1.0]})
#                 safe_xai = st.session_state.get('xai_data', fallback_xai)
#
#                 st.session_state['gov_report'] = generate_gov_report(vision_res, safe_xai,
#                                                                      st.session_state['emergency_val'])
#
#             status.update(label="报告生成完毕！", state="complete", expanded=False)
#
#         with st.container(border=True):
#             st.markdown("### 📄 《微流域水质突发异常情况专报》")
#             st.info(st.session_state['gov_report'])
#             st.download_button("一键下载 (Word)", st.session_state['gov_report'], file_name="应急专报.docx")
#
#         if st.button("处置完毕，解除预警"):
#             del st.session_state['trigger_emergency_report']
#             st.rerun()
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