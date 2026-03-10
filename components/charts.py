import plotly.graph_objects as go
import pydeck as pdk
import pandas as pd


def draw_task_map(df_tasks):
    fig_map = go.Figure(go.Scattermapbox(
        lat=df_tasks['lat'], lon=df_tasks['lon'], mode='markers',
        marker=go.scattermapbox.Marker(size=16, color='#dc2626', opacity=0.9),
        text=df_tasks['loc'] + "：" + df_tasks['desc'], hoverinfo='text'
    ))
    fig_map.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[{
            "below": 'traces', "sourcetype": "raster",
            "source": ["https://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7"]
        }],
        mapbox=dict(center=dict(lat=29.2, lon=120.1), zoom=6.5),
        margin=dict(l=0, r=0, t=0, b=0), height=350, paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig_map


def draw_evo_chart(df, curr_metric):
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        x=df['Date'], y=df[curr_metric], fill='tozeroy', mode='lines',
        line=dict(color='#3b82f6', width=2), fillcolor='rgba(59, 130, 246, 0.2)'
    ))
    fig_evo.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=220,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickformat="%m月%d日", hoverformat="%Y年%m月%d日"),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    return fig_evo

def draw_gauge_chart(twin_gate_open_pct, twin_pump_load):
    # 稍微回调一点点字号，保证美观
    title_font = {'size': 13, 'color': '#0f172a', 'family': 'sans-serif'}
    num_font = {'size': 22, 'color': '#1e3a8a'}

    fig_gauge = go.Figure()

    # 【1】左上：土壤饱和度
    # 修改 x 为 [0.05, 0.45]，让出左边缘
    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number", value=82,
        title={'text': "<b>土壤饱和度(%)</b>", 'font': title_font},
        number={'font': num_font},
        gauge={'axis': {'range': [0, 100], 'showticklabels': False}, 'bar': {'color': "#3b82f6"}},
        domain={'x': [0.05, 0.45], 'y': [0.65, 1.0]}
    ))

    # 【2】右上：水闸开启度
    # 修改 x 为 [0.55, 0.95]，不要贴死 1.0，防止文字向右溢出排版
    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number", value=twin_gate_open_pct,
        title={'text': "<b>水闸开启度(%)</b>", 'font': title_font},
        number={'font': num_font},
        gauge={'axis': {'range': [0, 100], 'showticklabels': False},
               'bar': {'color': "#10b981" if twin_gate_open_pct > 0 else "#ef4444"}},
        domain={'x': [0.55, 0.95], 'y': [0.65, 1.0]}
    ))

    # 【3】左下：泵站负荷
    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number", value=twin_pump_load,
        title={'text': "<b>泵站负荷(%)</b>", 'font': title_font},
        number={'font': num_font},
        gauge={'axis': {'range': [0, 100], 'showticklabels': False},
               'bar': {'color': "#f59e0b" if twin_pump_load < 90 else "#ef4444"}},
        domain={'x': [0.05, 0.45], 'y': [0.0, 0.35]}
    ))

    # 【4】右下：管网压力
    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number", value=45,
        title={'text': "<b>管网压力(kPa)</b>", 'font': title_font},
        number={'font': num_font},
        gauge={'axis': {'range': [0, 100], 'showticklabels': False}, 'bar': {'color': "#8b5cf6"}},
        domain={'x': [0.55, 0.95], 'y': [0.0, 0.35]}
    ))

    fig_gauge.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig_gauge


def draw_radar_chart():
    radar_fig = go.Figure()
    radar_fig.add_trace(
        go.Scatterpolar(r=[7.2, 6.5, 2.5, 3.1, 4.0], theta=['酸碱', '溶解氧', '氨氮', '总磷', '浊度'], fill='toself',
                        line_color='#1e3a8a', fillcolor='rgba(30, 64, 175, 0.2)'))
    radar_fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 15]), bgcolor='rgba(0,0,0,0)'),
                            paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#1e3a8a', size=11),
                            margin=dict(l=15, r=15, t=15, b=15), height=180, showlegend=False)
    return radar_fig


def draw_pydeck_map(geo_df):
    view_state = pdk.ViewState(latitude=29.2, longitude=120.1, zoom=6.2, pitch=45)
    geojson = pdk.Layer("GeoJsonLayer", data="https://geo.datav.aliyun.com/areas_v3/bound/330000_full.json",
                        stroked=True, filled=True, get_fill_color=[241, 245, 249], get_line_color=[30, 58, 138],
                        line_width_min_pixels=2)
    columns = pdk.Layer('ColumnLayer', data=geo_df, get_position='[lon, lat]', get_elevation='elevation',
                        elevation_scale=1, radius=9000, get_fill_color='color', pickable=True)
    return pdk.Deck(layers=[geojson, columns], initial_view_state=view_state, map_provider=None,
                    tooltip={"text": "{station}\n指标: {ph_level}"})



def draw_pred_chart(past_dates, past_vals, future_dates, pred_y):
    fig_pred = go.Figure()

    # 1. 绘制历史真实数据
    fig_pred.add_trace(go.Scatter(x=past_dates, y=past_vals, mode='lines+markers', name='历史真实数据',
                                  line=dict(color='#3b82f6', width=2)))

    # 2. 拼接预测走势数据（修正部分）
    # X轴：[历史最后一天日期] + [未来预测日期]
    pred_x = [past_dates.iloc[-1]] + list(future_dates)

    # Y轴：[历史最后一个真实值] + [未来预测值]
    pred_y_connected = [past_vals.iloc[-1]] + list(pred_y)

    # 3. 绘制 AI 推演走势
    fig_pred.add_trace(go.Scatter(x=pred_x, y=pred_y_connected, mode='lines+markers', name='AI推演走势',
                                  line=dict(color='#ef4444', width=2, dash='dash')))

    fig_pred.update_layout(height=230, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(tickformat="%m月%d日", hoverformat="%Y年%m月%d日"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig_pred
def draw_xai_pie(xai_df):
    fig_xai = go.Figure(data=[
        go.Pie(labels=xai_df['污染归因要素'], values=xai_df['权重贡献度'], hole=.45, textinfo='label+percent',
               textposition='outside', textfont=dict(size=14, color='#1e293b', family="Arial, sans-serif"),
               marker=dict(colors=['#ef4444', '#f59e0b', '#10b981', '#3b82f6'], line=dict(color='#ffffff', width=2)))])
    fig_xai.update_layout(height=260, margin=dict(l=40, r=40, t=15, b=40), showlegend=False,
                          paper_bgcolor='rgba(0,0,0,0)')
    return fig_xai
