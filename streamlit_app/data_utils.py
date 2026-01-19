import pandas as pd
import streamlit as st
import os
import joblib

DATA_PATH = "data"
MODEL_PATH = "models/churn_model.pkl"

@st.cache_data(ttl=3600)
def load_all_data():
    tables = {}
    files = ['dim_users', 'dim_levels', 'fact_sessions', 'fact_gameplay_events', 'fact_monetization',
             'fact_technical_health']
    for f in files:
        path = os.path.join(DATA_PATH, f"{f}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            for col in ['install_date', 'start_time', 'end_time', 'timestamp']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            tables[f] = df
        else:
            tables[f] = pd.DataFrame()
    return tables


def get_retention_matrix(df_sessions, df_users):
    """Xây dựng ma trận Cohort Retention."""
    if df_sessions.empty or df_users.empty: return pd.DataFrame()

    # 1. Join lấy install_date
    df = pd.merge(df_sessions, df_users[['user_id', 'install_date']], on='user_id')

    # 2. Tính Day Diff (D0, D1, D3, D7...)
    df['day_diff'] = (df['start_time'].dt.date - df['install_date'].dt.date).dt.days

    # 3. Chỉ lấy dữ liệu trong 30 ngày đầu để ma trận gọn đẹp
    df = df[(df['day_diff'] >= 0) & (df['day_diff'] <= 30)]

    # 4. Tạo bảng Pivot đếm User
    cohort_data = df.groupby(['install_date', 'day_diff'])['user_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='install_date', columns='day_diff', values='user_id')

    # 5. Tính tỷ lệ % Retention (Chia cho cột Day 0)
    retention_matrix = cohort_pivot.divide(cohort_pivot.iloc[:, 0], axis=0)

    # Lưu kích thước cohort gốc để làm tooltip (tuỳ chọn)
    cohort_size = cohort_pivot.iloc[:, 0]

    return retention_matrix, cohort_size
