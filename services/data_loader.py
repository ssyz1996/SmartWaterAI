import pandas as pd
import numpy as np
import streamlit as st
import duckdb
import time


@st.cache_data(ttl=60)
def load_timeseries_data(god_mode, interval='6 hours', limit=90):
    start_q_time = time.time()

    # 获取底库真实的物理行数 (DuckDB 查 count 是瞬间完成的)
    total_rows = duckdb.query("SELECT COUNT(*) FROM 'data/water_history.parquet'").fetchone()[0]
    st.session_state['duckdb_total_rows'] = total_rows  # 存入全局状态供大屏显示

    # 动态构建真实的大数据 OLAP 聚合 SQL
    query = f"""
        SELECT 
            time_bucket(INTERVAL '{interval}', timestamp) AS Date,
            AVG(ph_level) AS 酸碱,
            AVG(do_level) AS 溶解氧,
            AVG(nh3n_level) AS 氨氮,
            AVG(tp_level) AS 总磷,
            AVG(turbidity) AS 浊度
        FROM 'data/water_history.parquet'
        GROUP BY Date
        ORDER BY Date DESC
        LIMIT {limit}
    """

    # 极速向量化执行
    df = duckdb.query(query).to_df()
    df = df.sort_values('Date').reset_index(drop=True)

    end_q_time = time.time()

    # 🌟 核心：把底层的大数据执行指标存起来，给大屏展示用
    st.session_state['duckdb_cost'] = round((end_q_time - start_q_time) * 1000, 2)
    st.session_state['duckdb_sql'] = query
    st.session_state['duckdb_rows'] = len(df)

    if god_mode:
        last_idx = len(df) - 1
        df.loc[last_idx - 2:last_idx, '酸碱'] = [8.1, 8.8, 9.6]
        df.loc[last_idx - 2:last_idx, '溶解氧'] = [5.0, 4.2, 3.1]
        df.loc[last_idx - 2:last_idx, '氨氮'] = [0.8, 1.2, 1.8]
        df.loc[last_idx - 2:last_idx, '总磷'] = [0.3, 0.5, 0.8]
        df.loc[last_idx - 2:last_idx, '浊度'] = [8.0, 12.5, 18.2]

    return df

@st.cache_data
def load_geo_data(god_mode):
    ph_levels, colors, elevations = [7.1, 7.2, 6.9, 7.3, 7.5, 7.2, 6.8], [[30, 64, 175, 220] for _ in range(7)], [15000, 35000, 12000, 18000, 20000, 14000, 11000]
    if god_mode:
        ph_levels[1], colors[1], elevations[1] = 9.6, [185, 28, 28, 255], 90000
    return pd.DataFrame({
        "station": ["杭州-新安江", "宁波-姚江", "温州-飞云江", "绍兴-曹娥江", "金华-婺江", "衢州-衢江", "丽水-瓯江"],
        "lat": [29.6, 29.87, 27.99, 30.0, 29.08, 28.97, 28.45],
        "lon": [119.2, 121.54, 120.69, 120.58, 119.64, 118.86, 119.92], 
        "ph_level": ph_levels, "color": colors, "elevation": elevations
    })