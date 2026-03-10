import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_timeseries_data(god_mode):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=60)
    x = np.linspace(0, 15, 60)

    df = pd.DataFrame({
        'Date': dates,
        '酸碱': 7.2 + np.sin(x) * 0.3 + np.random.normal(0, 0.08, 60),
        '溶解氧': 6.5 + np.cos(x) * 0.5 + np.random.normal(0, 0.15, 60),
        '氨氮': 0.45 + np.sin(x * 1.5) * 0.1 + np.random.normal(0, 0.05, 60),
        '总磷': 0.12 + np.cos(x * 1.2) * 0.03 + np.random.normal(0, 0.01, 60),
        '浊度': 3.5 + np.sin(x * 0.8) * 0.5 + np.random.normal(0, 0.2, 60)
    })

    if god_mode:
        df.loc[57:59, '酸碱'] = [8.1, 8.8, 9.6]
        df.loc[57:59, '溶解氧'] = [5.0, 4.2, 3.1]
        df.loc[57:59, '氨氮'] = [0.8, 1.2, 1.8]
        df.loc[57:59, '总磷'] = [0.3, 0.5, 0.8]
        df.loc[57:59, '浊度'] = [8.0, 12.5, 18.2]
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