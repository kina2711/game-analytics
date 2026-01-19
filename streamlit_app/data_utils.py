import pandas as pd
import streamlit as st
import os

@st.cache_data(ttl=3600)
def load_all_data():
    tables = {}
    files = ['dim_users', 'dim_levels', 'fact_sessions', 'fact_gameplay_events', 'fact_monetization',
             'fact_technical_health']
    for f in files:
        df = pd.read_csv(f"data/{f}.csv")
        # Chuẩn hóa thời gian
        for col in ['install_date', 'start_time', 'end_time', 'timestamp']:
            if col in df.columns: df[col] = pd.to_datetime(df[col])
        tables[f] = df
    return tables

def apply_filters(tables, countries, platforms, versions):
    # Logic lọc dữ liệu dùng chung cho các trang
    u = tables['dim_users']
    mask = u['country'].isin(countries) & u['platform'].isin(platforms)
    u_filtered = u[mask]

    # Lọc các bảng fact theo danh sách user đã lọc
    u_ids = u_filtered['user_id']
    filtered_tables = {'dim_users': u_filtered}
    for k in ['fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']:
        df = tables[k]
        f_df = df[df['user_id'].isin(u_ids)]
        if 'app_version' in f_df.columns:
            f_df = f_df[f_df['app_version'].isin(versions)]
        filtered_tables[k] = f_df
    return filtered_tables