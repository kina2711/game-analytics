import pandas as pd
import streamlit as st
import os
import joblib

DATA_PATH = "data"
MODEL_PATH = "models/churn_model.pkl"

@st.cache_data(ttl=3600)
def load_all_data():
    """Đọc dữ liệu và chuẩn hóa thời gian."""
    tables = {}
    files = ['dim_users', 'dim_levels', 'fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']
    for f in files:
        path = os.path.join(DATA_PATH, f"{f}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Ép kiểu datetime an toàn cho toàn bộ project
            for col in ['install_date', 'start_time', 'timestamp']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            tables[f] = df
        else:
            tables[f] = pd.DataFrame()
    return tables

def apply_filters(tables, countries, platforms, date_range):
    """Lọc dữ liệu theo quốc gia, nền tảng và khoảng ngày cài đặt."""
    u = tables['dim_users']
    if u.empty: return tables
    
    # Filter theo ngày (Dataset từ 01/11/2025 đến 30/11/2025)
    mask = (u['country'].isin(countries)) & \
           (u['platform'].isin(platforms)) & \
           (u['install_date'].dt.date >= date_range[0]) & \
           (u['install_date'].dt.date <= date_range[1])
    
    u_filtered = u[mask]
    u_ids = u_filtered['user_id'].unique()
    
    filtered_tables = {'dim_users': u_filtered, 'dim_levels': tables['dim_levels']}
    for k in ['fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']:
        df = tables[k]
        filtered_tables[k] = df[df['user_id'].isin(u_ids)]
        
    return filtered_tables

def get_full_cohort_matrix(df_sessions, df_users):
    """Xử lý ma trận Cohort 7 ngày."""
    if df_sessions.empty or df_users.empty: return pd.DataFrame()

    df = pd.merge(df_sessions[['user_id', 'start_time']], 
                  df_users[['user_id', 'install_date']], on='user_id')
    
    # Tính số ngày chênh lệch
    df['day_diff'] = (df['start_time'].dt.date - df['install_date'].dt.date).apply(lambda x: x.days)
    df = df[(df['day_diff'] >= 0) & (df['day_diff'] <= 7)]

    # Tính quy mô từng nhóm (Cohort Size)
    cohort_sizes = df_users.groupby('install_date')['user_id'].nunique().reset_index()
    cohort_sizes.columns = ['Date', 'Total Users']

    # Tạo ma trận % retention
    matrix = df.groupby(['install_date', 'day_diff'])['user_id'].nunique().unstack(fill_value=0)
    retention_matrix = matrix.divide(matrix[0], axis=0)
    
    # Hợp nhất dữ liệu
    result = cohort_sizes.set_index('Date').join(retention_matrix)
    result.index = result.index.strftime('%d %b') 
    return result

def predict_churn(is_crash, fps_avg, level_id):
    """Hàm dự báo Churn."""
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            features = pd.DataFrame([[is_crash, fps_avg, level_id]], 
                                   columns=['is_crash', 'fps_avg', 'level_id'])
            return model.predict_proba(features)[0][1]
        except: return None
    return None
