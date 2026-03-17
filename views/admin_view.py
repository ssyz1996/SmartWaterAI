import streamlit as st
import pandas as pd
import hashlib
from openai import OpenAI
from config import settings
from components.charts import (draw_evo_chart, draw_gauge_chart, draw_radar_chart, draw_pydeck_map, draw_pred_chart,
                               draw_xai_pie)
from components.custom_html import (get_node_html, get_empty_ledger_html, get_topology_html, get_twin_html,
                                    get_logs_html)
from services.ai_core import WaterQualityMLPredictor
from services.llm_service import analyze_citizen_photo,  generate_gov_report


def render_admin_view(df, geo_df, target_obj, ml_algorithm, future_days, start_btn):
    # --- 1. 顶部指标 ---
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        # 显示真实的底层数据湖查询速度
        cost_ms = st.session_state.get('duckdb_cost', 15.2)
        st.metric("💾 湖仓OLAP聚合耗时", f"{cost_ms} ms", "扫描1,000,000条底库")
    with k2:
        st.metric(f"💧 {target_obj} 极值", f"{df[target_obj].iloc[-1]:.2f}",
                  "+2.40!" if st.session_state['god_mode'] else "稳定",
                  delta_color="inverse" if st.session_state['god_mode'] else "normal")
    with k3:
        st.metric("🔗 链上存证量", f"{len(st.session_state.blockchain_logs)} 笔",
                  "FISCO BCOS 底层")
    with k4:
        st.metric("🏭 涉水监控", "3,105", "12家异常")
    with k5:
        st.metric("🧠 算力状态", "24.5%", "运行健康")

    # --- 2. 区块链数据信任确权中心 ---
    st.markdown("### 🔗 Web3.0 区块链数据信任确权中心")
    bc_col1, bc_col2, bc_col3 = st.columns([1.1, 1.7, 1.1])
    fake_hashes = "<br>".join([hashlib.sha256(str(i).encode()).hexdigest()[:24] for i in range(40)])

    with bc_col1:
        st.markdown(get_node_html(12045 + len(st.session_state.blockchain_logs), len(st.session_state.blockchain_logs),
                                  fake_hashes), unsafe_allow_html=True)
    with bc_col2:
        if not st.session_state.blockchain_logs:
            st.markdown(get_empty_ledger_html(), unsafe_allow_html=True)
        else:
            blocks_html = ""
            for i, log in enumerate(st.session_state.blockchain_logs[:3]):
                is_latest = (i == 0)
                border_style = "2px solid #3b82f6" if is_latest else "1px solid #cbd5e1"
                bg_color = "#eff6ff" if is_latest else "#ffffff"
                badge = "<span style='background:#3b82f6; color:white; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:bold; position:absolute; top:-8px; right:15px;'>🌟 最新生成区块</span>" if is_latest else ""

                # ⚠️ 修正核心：这里的 HTML 必须严格顶格写，没有任何前面的空格
                blocks_html += f"""<div style="background: {bg_color}; border: {border_style}; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
{badge}
<div style="display:flex; justify-content:space-between; font-size:12px; color:#64748b; margin-bottom:8px;"><span style="font-family:monospace;">{log['time']}</span><span style="font-weight:bold; color:#1e293b;">{log['operator']}</span></div>
<div style="font-weight:bold; color:#0f172a; font-size:13px; margin-bottom:6px;"><span style="color:#ef4444; background:#fee2e2; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:5px;">核心指令</span> {log['action']}</div>
<div style="color:#475569; font-size:11px; margin-bottom:6px; line-height:1.4;"><span style="font-weight:bold;">执行详情：</span>{log.get('desc', '已在全网广播')}</div>
<div style="background:#f1f5f9; padding:6px 8px; border-radius:6px; font-family:monospace; font-size:11px; color:#64748b; display:flex; justify-content:space-between; align-items:center;">
<span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:75%;"><span style="color:#3b82f6; font-weight:bold;">TxHash:</span> {log['tx_hash']}</span><span style="color:#10b981; font-weight:900;">🔗 已确权</span></div>
</div>"""
                if i < min(len(st.session_state.blockchain_logs), 3) - 1:
                    blocks_html += """<div style="text-align:center; color:#94a3b8; font-size:14px; margin-bottom:6px; line-height:1;">⬇</div>"""

            st.markdown(
                f'<div class="bc-card" style="overflow-y: auto;"><div style="position: sticky; top: -15px; background: rgba(255,255,255,0.95); backdrop-filter: blur(5px); padding: 0 0 10px 0; margin-top: -5px; z-index: 10; border-bottom: 1px dashed #e2e8f0; margin-bottom: 12px;"><span style="font-weight:900; color:#1e3a8a; font-size:16px;">⛓️ 实时分布式账本 (Ledger)</span></div>{blocks_html}</div>',
                unsafe_allow_html=True)

    with bc_col3:
        st.markdown(get_topology_html(), unsafe_allow_html=True)
    st.markdown("---")

    # --- 3. 演化图与仪表盘 ---
    # ================= 炫技专区：大数据引擎实时遥测 =================
    st.markdown("### 基于 DuckDB 向量化引擎的湖仓一体动态遥测 (Lakehouse)")
    with st.container(border=True):
        db_c1, db_c2, db_c3, db_c4 = st.columns(4)

        # 🌟 获取真实的底层行数，并格式化为带逗号的字符串 (如 "671,438")
        real_total_rows = st.session_state.get('duckdb_total_rows', 0)
        formatted_rows = f"{real_total_rows:,}"

        db_c1.metric("📦 底层 Parquet 扫描规模", f"{formatted_rows} 条", "含1.74%物理丢包")
        db_c2.metric("⚡ 引擎冷启动/聚合耗时", f"{st.session_state.get('duckdb_cost', 0)} ms", "毫秒级零延迟极速响应")
        db_c3.metric("🧮 当前动态聚合粒度", st.session_state.get('db_interval', '6 hours'), "流批一体时间切片")
        db_c4.metric("📊 实际渲染降采样节点", st.session_state.get('duckdb_rows', 90), "输出至大屏与 AI 推演")

        with st.expander("👁️ 查看底层实时执行的 OLAP 聚合 SQL 语句", expanded=False):
            st.code(st.session_state.get('duckdb_sql', '-- 暂无查询记录'), language='sql')
    # ==============================================================
    col_top_left, col_top_right = st.columns([1.5, 1])
    with col_top_left:
        with st.container(border=True):
            st.markdown("#### 湖仓一体 OLAP 实时动态聚合")
            metrics_list = ["酸碱", "溶解氧", "氨氮", "总磷", "浊度"]
            tabs = st.tabs(metrics_list)
            for i, tab in enumerate(tabs):
                with tab: st.plotly_chart(draw_evo_chart(df, metrics_list[i]), use_container_width=True)

    with col_top_right:
        with st.container(border=True):
            st.markdown("#### 🌊 核心协同设备参数")
            is_emergency = st.session_state.get('god_mode', False)
            twin_gate_open_pct = 0 if is_emergency else 85
            twin_pump_load = 92 if is_emergency else 68
            st.plotly_chart(draw_gauge_chart(twin_gate_open_pct, twin_pump_load), use_container_width=True)

            gate_nodes = [
                {"name": "杭州新安江·Z1", "n_open": 85, "e_open": 30, "n_flow": "125.4", "e_flow": "42.1",
                 "casing": "#e2e8f0", "border": "#64748b", "water": "linear-gradient(180deg, #60a5fa 0%, #1e3a8a 100%)",
                 "gate": "linear-gradient(90deg, #94a3b8 0%, #cbd5e1 50%, #94a3b8 100%)", "gate_border": "#f59e0b"},
                {"name": "宁波姚江·Z2", "n_open": 80, "e_open": 0, "n_flow": "98.2", "e_flow": "0.0",
                 "casing": "#f8fafc", "border": "#475569", "water": "linear-gradient(180deg, #34d399 0%, #047857 100%)",
                 "gate": "linear-gradient(90deg, #fbbf24 0%, #fcd34d 50%, #fbbf24 100%)", "gate_border": "#d97706"},
                {"name": "温州飞云江·Z3", "n_open": 90, "e_open": 20, "n_flow": "156.0", "e_flow": "28.5",
                 "casing": "#cbd5e1", "border": "#334155", "water": "linear-gradient(180deg, #38bdf8 0%, #0c4a6e 100%)",
                 "gate": "linear-gradient(90deg, #a1a1aa 0%, #e4e4e7 50%, #a1a1aa 100%)", "gate_border": "#52525b"}
            ]
            gates_html_content = ""
            for i, node in enumerate(gate_nodes):
                c_open = node['e_open'] if is_emergency else node['n_open']
                c_flow = node['e_flow'] if is_emergency else node['n_flow']
                stat_c, stat_t, g_top = ("#ef4444", "🚨 紧急锁死", "0%") if c_open == 0 else (
                    ("#f59e0b", "🟡 压减泄洪", f"-{c_open}%") if c_open < 50 else (
                    "#10b981", "🟢 自动调度", f"-{c_open}%"))
                gates_html_content += f"""
                <div style="flex: 1; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.08); margin: 0 4px; display: flex; flex-direction: column;">
                <div style="font-size: 11px; font-weight: 800; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px; text-align: center;">{node['name']}</div>
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                <div style="width: 60px; height: 85px; background: {node['casing']}; position: relative; overflow: hidden; border-left: 6px solid {node['border']}; border-right: 6px solid {node['border']}; border-top: 6px solid #1e293b; border-radius: 3px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
                <div style="position: absolute; bottom: 0; width: 100%; height: 55%; background: {node['water']}; z-index: 1;"></div>
                <div style="position: absolute; top: {g_top}; left: 0; width: 100%; height: 100%; background: {node['gate']}; border-bottom: 4px solid {node['gate_border']}; z-index: 2; transition: top 1.2s cubic-bezier(0.4, 0, 0.2, 1); display: flex; flex-direction: column; justify-content: space-evenly; align-items: center;">
                <div style="width: 100%; height: 2px; background: rgba(0,0,0,0.2); box-shadow: 0 1px 1px rgba(255,255,255,0.4);"></div><div style="width: 100%; height: 2px; background: rgba(0,0,0,0.2); box-shadow: 0 1px 1px rgba(255,255,255,0.4);"></div>
                </div></div>
                <div style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #475569; line-height: 1.6;">
                <div style="color: {stat_c}; font-weight: 900; font-family: sans-serif; font-size: 13px; margin-bottom: 4px;">{stat_t}</div>
                <div>开度:<span style="color: #0284c7; font-weight: 900; font-size: 14px; margin-left: 2px;">{c_open}%</span></div>
                <div>流量:<span style="color: #334155; font-weight: bold; margin-left: 2px;">{c_flow}</span></div>
                </div></div></div>"""
            st.markdown(get_twin_html(gates_html_content), unsafe_allow_html=True)

    # --- 4. 雷达图、日志与地图 ---
    col_bot_left, col_bot_right = st.columns([1, 2.2])
    with col_bot_left:
        with st.container(border=True):
            st.markdown("#### 🎯 水质生态雷达")
            st.plotly_chart(draw_radar_chart(), use_container_width=True)

        with st.container(border=True):
            st.markdown("#### 📜 系统指令流日志")
            logs_data = ["10:42 🟢 [温州飞云江] 泵站P2运行平稳，流量正常",
                         "10:35 🟡 [杭州新安江] 浊度轻微上升，已开启AI关注",
                         "10:12 🟢 [绍兴曹娥江] 水闸Z1已执行自动化关闭", "09:58 🟢 [金华婺江] 溶解氧恢复至正常区间(>5.0)",
                         "09:30 🔵 [系统内核] XAI周期性特征自适应校准完成", "09:15 🟢 [宁波姚江] 近岸水位监测点读数正常",
                         "08:45 🔵 [社会端] 收到 12 条有效公众上报巡检记录"]
            if st.session_state['god_mode']:
                logs_data.insert(0, "10:45 🔒 [区块链存证] 智能合约已将本次【AI协同控制命令】永久上链！")
                logs_data.insert(1, "10:45 🚨 [硬件接管] 智能体已接管底层 PLC，Z2 主控水闸执行紧急锁死！")
                logs_data.insert(2, "10:45 🚨 [污染报警] 物联网节点发现【宁波姚江】数据突变，大模型介入拦截！")

            inner_html = ""
            for log in logs_data:
                color = "#dc2626" if "🚨" in log else (
                    "#8b5cf6" if "🔒" in log else ("#d97706" if "🟡" in log else "#1e3a8a"))
                weight = "bold" if ("🚨" in log or "🔒" in log) else "normal"
                inner_html += f"<div style='color:{color}; font-weight:{weight}; border-bottom:1px dashed #cbd5e1; padding-bottom:3px; margin-bottom:3px;'>{log}</div>"
            st.markdown(get_logs_html(inner_html), unsafe_allow_html=True)

    with col_bot_right:
        with st.container(border=True):
            # 1. 创建一个空容器占位符
            map_placeholder = st.empty()

            # 2. 生成地图对象
            deck_obj = draw_pydeck_map(geo_df)

            # 3. 在容器中渲染地图（不传 key 参数，避开版本兼容问题）
            map_placeholder.pydeck_chart(deck_obj, use_container_width=True)
    st.markdown("---")

#TODO ACTION 1 系统开发工程师-后端开发部分
    # *************************** 实操环节 - part1：王彦霆 - 系统开发工程师****************************************************
    # —— 状态管理与数据总线串联
    # 全局异常数据总线监控与联动触发
    # 1. 实例化一个基础的预测器（仅用于调用异常检测方法）
    anomaly_checker = WaterQualityMLPredictor()
# TODO ACTION 2 系统开发工程师-后端开发部分
    # 2. 实时检测当前选中的指标 (target_obj) 是否发生数据突变

    # ACTION 1 版本代码：
    is_anomaly, val = anomaly_checker.detect_sudden_anomaly(df, target_obj)

    # ACTION 2 版本代码 开始： (台上实操时解开注释，解决解包 ValueError 报错)：
    # is_anomaly, val, current_esi = anomaly_checker.detect_sudden_anomaly(df, target_obj)
    # st.session_state['emergency_esi'] = current_esi  # 存入全局总线，给大模型用
    # ACTION 2 版本代码 结束


    # 3. 当检测到异常（例如被“紧急预警”按钮触发 God Mode），且尚未生成报告时
    if is_anomaly and 'report_generated' not in st.session_state:
        st.session_state['trigger_emergency_report'] = True
        st.session_state['emergency_val'] = val

    # *************************** 实操环节 - part1：王彦霆 - 系统开发工程师****************************************************


    if start_btn:
        model_key = ml_algorithm.split(" ")[0]
        predictor = WaterQualityMLPredictor(model_type=model_key)
        st.session_state.update({
            'future_vals': predictor.train_and_predict(df, target_col=target_obj, future_steps=future_days),
            'target_obj': target_obj, 'future_days': future_days
        })
        if model_key in ['RF', 'GBDT', 'DT']:
            st.session_state['xai_data'] = predictor.get_xai_feature_importance()
        elif 'xai_data' in st.session_state:
            del st.session_state['xai_data']

    if st.session_state.get('citizen_report'):
        st.markdown("<h3 style='color:#dc2626;'>🚨 多模态 AI 紧急拦截舱</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1: st.image("photo/水.jpg", caption="公众随手拍现场照片")
            with c2:
                with st.spinner("AI 视觉大模型正在解析图像..."): analysis = analyze_citizen_photo("photo/水.jpg")
                st.error(f"⚠️ **AI 视觉预警**：检测到 {analysis['pollution_type']}")
                st.warning(f"📉 **量化评级**：危险指数 {analysis['severity_score']}/10.0")
                st.info(f"💡 **AI 建议**：{analysis['ai_suggestion']}")
                if st.button("🚀 采纳 AI 建议，一键派发基层巡检员", type="primary"):
                    st.session_state.task_list.insert(0, {"time": "刚刚", "loc": "公众上报隐患点",
                                                          "desc": f"【AI协同工单】{analysis['pollution_type']}",
                                                          "status": "紧急待办", "user": "多模态智水Agent",
                                                          "lat": 29.6001, "lon": 119.2005})
                    st.toast("✅ 派单成功！")
                    st.session_state['citizen_report'] = False

    if 'future_vals' in st.session_state:
        p_col, x_col = st.columns([1.5, 1])
        with p_col:
            with st.container(border=True):
                st.markdown("#### 🧠 AI 多维时序预测推演")
                past_dates, past_vals = df['Date'].iloc[-14:], df[st.session_state['target_obj']].iloc[-14:]
                future_dates = pd.date_range(start=df['Date'].iloc[-1] + pd.Timedelta(days=1),
                                             periods=len(st.session_state['future_vals']))
                st.plotly_chart(draw_pred_chart(past_dates, past_vals, future_dates, st.session_state['future_vals']),
                                use_container_width=True)
        with x_col:
            with st.container(border=True):
                st.markdown("#### 💡 核心异动溯源归因")
                if 'xai_data' in st.session_state:
                    st.plotly_chart(draw_xai_pie(st.session_state['xai_data']), use_container_width=True)
                else:
                    st.info("💡 请在左侧侧边栏切换至树模型 (RF/GBDT/DT) 开启可解释归因分析")

    # --- 6. 多智能体助手与专报 ---
    with st.container(border=True):
        st.markdown("#### 🤖 水宝智能AI助手 Smart AI Assistant")

        LLM_API_KEY = "sk-51004d500a0146c0acfd2764b25d7f65"
        LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        LLM_MODEL_NAME = "qwen-plus"

        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("下达研判指令... (例如：分析当前水质情况，并给出治理建议)")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            latest_ph = df['酸碱'].iloc[-1]
            latest_do = df['溶解氧'].iloc[-1]
            latest_nh3n = df['氨氮'].iloc[-1]
            latest_tp = df['总磷'].iloc[-1]
            latest_turb = df['浊度'].iloc[-1]

            status_text = "【紧急突发状态：水质严重异常！】" if st.session_state['god_mode'] else "【平稳正常】"
            tasks_info = "\n".join([f"- 位置:{t['loc']} | 描述:{t['desc']} | 状态:{t['status']}" for t in
                                    st.session_state.task_list]) if st.session_state.task_list else "暂无公众上报事件"

            system_prompt = f"""
                    你是一个名为"浙江政务 Data Copilot"的智慧水务数字孪生AI助手。
                    请严格基于以下【实时监测数据】回答用户的研判指令：
                    [当前流域整体状态]：{status_text}
                    [最新实时水质指标]：酸碱度={latest_ph:.2f}, 溶解氧={latest_do:.2f}mg/L, 氨氮={latest_nh3n:.2f}mg/L, 总磷={latest_tp:.2f}mg/L, 浊度={latest_turb:.2f}NTU
                    [待处理公众上报工单]：
                    {tasks_info}
            回答要求：
            1. 语气必须是专业、严谨的政务决策辅助口吻，排版清晰美观。
            2. 如果发现水质异常，必须立刻给出应急处置与溯源排查建议。
            """

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                try:
                    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                    response = client.chat.completions.create(
                        model=LLM_MODEL_NAME, messages=api_messages, stream=True,
                    )
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"⚠️ **系统提示**：连接失败。\n\n*错误：{str(e)}*"
                    message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})

#TODO ACTION 1 系统开发工程师-前端开发部分
    # *************************** 实操环节 - Action 1 开始：系统开发工程师-前端****************************************************
    # 状态管理与数据总线串联
    # 交互开发与全局总控
    # 角色定位：一边给评委解说，一边开发最酷炫的前端交互——“指挥舱紧急状态弹窗”。
    # 现场开发：利用 Streamlit 最新特性（如 st.status 或 st.dialog），展示报告生成的动态过程，并提供一键下载按钮。
    if st.session_state.get('trigger_emergency_report'):
        st.markdown("---")
        st.error("系统侦测到严重水质突变，自动研判预警机制已启动！")

        with st.status("多智能体协同正在撰写水质专报...", expanded=True) as status:
            st.write("1. 调取时序突变检测算法...")
            st.write("2. 融合多模态视觉溯源...")
            st.write("3. 提取归因权重分布...")

            # 传入之前缓存的数据生成报告
            if 'gov_report' not in st.session_state:
                # 假定 vision_res 已经存储在 session 中
                vision_res = st.session_state.get('vision_res',
                                                  {'pollution_type': '水面大面积漂浮物', 'severity_score': 8.5})

                # 🌟 修复：防止没有先点击AI预测导致的 KeyError
                fallback_xai = pd.DataFrame({"污染归因要素": ["工业偷排或面源污染(兜底推测)"], "权重贡献度": [1.0]})
                safe_xai = st.session_state.get('xai_data', fallback_xai)

                # 调用大模型生成专报
                st.session_state['gov_report'] = generate_gov_report(vision_res, safe_xai,
                                                                     st.session_state['emergency_val'])

            status.update(label="报告生成完毕！", state="complete", expanded=False)

        with st.container(border=True):
# TODO ACTION 2  系统工程师
            # ACTION 1 改进前的代码
            st.markdown("### 《微流域水质突发异常情况专报》")
            st.info(st.session_state['gov_report'])

            # ACTION 2 开始
        #     #拿到4号传来的 ESI 指数 (前提是总线处也同步修改接收了 esi)
        #     current_esi = st.session_state.get('emergency_esi', 5.5)
        #     if current_esi > 5.0:
        #         st.error(f"🚨 警告：检测到极端气象恶化 (ESI指数: {current_esi})，启动防汛预案！")
        #
        #     stream_response = generate_gov_report(vision_res, safe_xai, st.session_state['emergency_val'], current_esi)
        #     st.session_state['gov_report'] = st.write_stream(stream_response) # 核心：渲染打字机动效
        #     # ACTION 2 结束
        #
        #     st.download_button("一键下载 (Word)", st.session_state['gov_report'], file_name="应急专报.docx")
        #
        # if st.button("处置完毕，解除预警"):
        #     del st.session_state['trigger_emergency_report']
        #     st.rerun()
    # *************************** Action 1 结束：系统开发工程师-前端****************************************************
