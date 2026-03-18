import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import os
from datetime import datetime

print("🚀 正在构建真实态泛在物联网数据湖...")

# 1. 严格遵守物理现实的时间戳 (近7年，每15分钟高频采样)
dates = pd.date_range(start='2019-01-01 00:00:00', end='2024-05-20 12:00:00', freq='15T')
n_timepoints = len(dates)

# 2. 真实的物理站点映射 (与系统前端的 7 个真实站点完全对齐)
stations = {
    "杭州-新安江": {"ph_base": 7.4, "do_base": 7.5, "turb_base": 2.5},
    "宁波-姚江": {"ph_base": 7.1, "do_base": 5.8, "turb_base": 4.5},
    "温州-飞云江": {"ph_base": 7.3, "do_base": 6.8, "turb_base": 3.0},
    "绍兴-曹娥江": {"ph_base": 7.2, "do_base": 6.2, "turb_base": 5.0},
    "金华-婺江": {"ph_base": 7.0, "do_base": 6.0, "turb_base": 4.0},
    "衢州-衢江": {"ph_base": 7.5, "do_base": 7.2, "turb_base": 2.0},
    "丽水-瓯江": {"ph_base": 7.6, "do_base": 8.0, "turb_base": 1.5}
}

df_list = []

for station, bases in stations.items():
    t_days = np.arange(n_timepoints) / (24 * 4)

    # 3. 引入随机游走 (布朗运动) 模拟长期的真实水质自然漂移
    drift_ph = np.cumsum(np.random.normal(0, 0.0015, n_timepoints))
    drift_do = np.cumsum(np.random.normal(0, 0.004, n_timepoints))

    # 季节循环与昼夜循环 (加入随机相位偏移)
    phase_shift = np.random.uniform(0, 2 * np.pi)
    seasonal = np.sin(2 * np.pi * t_days / 365 + phase_shift)
    diurnal = np.cos(2 * np.pi * t_days + phase_shift)

    # 计算基础指标（保留合理的小数位数，体现仪器精度）
    ph = bases["ph_base"] + 0.15 * seasonal + 0.05 * diurnal + drift_ph + np.random.normal(0, 0.03, n_timepoints)
    do = bases["do_base"] - 0.8 * seasonal + 0.4 * diurnal + drift_do + np.random.normal(0, 0.08, n_timepoints)
    nh3n = 0.45 + 0.1 * seasonal + np.random.normal(0, 0.04, n_timepoints)
    tp = 0.12 + 0.03 * seasonal + np.random.normal(0, 0.01, n_timepoints)
    turb = bases["turb_base"] + 1.2 * seasonal + np.random.normal(0, 0.4, n_timepoints)

    # 暴雨突发事件 (模拟台风天，每年大概遭遇 3-5 次剧烈波动)
    storm_indices = np.random.choice(n_timepoints - 200, size=12, replace=False)
    for idx in storm_indices:
        decay = np.exp(-np.arange(0, 96) / 24) # 暴雨影响持续 24 小时
        turb[idx:idx+96] += 12.0 * decay * np.random.uniform(0.8, 1.2)
        do[idx:idx+96] -= 2.5 * decay * np.random.uniform(0.8, 1.2)
        nh3n[idx:idx+96] += 0.9 * decay * np.random.uniform(0.8, 1.2)

    # 物理极限裁剪
    ph = np.clip(ph, 6.0, 9.0)
    do = np.clip(do, 1.0, 12.0)
    nh3n = np.clip(nh3n, 0.01, 3.0)
    tp = np.clip(tp, 0.01, 1.0)
    turb = np.clip(turb, 0.5, 50.0)

    # 组装本站点数据
    station_df = pd.DataFrame({
        'timestamp': dates,
        'station_id': station,
        'ph_level': np.round(ph, 2),
        'do_level': np.round(do, 2),
        'nh3n_level': np.round(nh3n, 3),
        'tp_level': np.round(tp, 3),
        'turbidity': np.round(turb, 1)
    })
    df_list.append(station_df)

# 合并全省 7 个站点数据
full_df = pd.concat(df_list, ignore_index=True)

# 4. 🌟 核心逼真操作：模拟物联网传感器掉线与网络丢包 (随机丢弃 1.74% 的数据)
print("📡 正在模拟边缘节点网络波动与数据丢包...")
full_df = full_df.sample(frac=0.9826, random_state=42).sort_values(by=['timestamp', 'station_id']).reset_index(drop=True)

# 处理绝对路径并保存
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(current_dir), 'data')
os.makedirs(data_dir, exist_ok=True)
save_path = os.path.join(data_dir, 'water_history.parquet')

table = pa.Table.from_pandas(full_df)
pq.write_table(table, save_path)

print(f"✅ 真实感湖仓数据编译完成！")
print(f"📊 最终有效历史存证条数：{len(full_df):,} 条 (含 1.74% 传感器物理丢包)")
print(f"💾 数据已稳固写入：{save_path}")