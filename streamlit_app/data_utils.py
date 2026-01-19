import pandas as pd
import streamlit as st
import os
import joblib

DATA_PATH = "data"
MODEL_PATH = "models/churn_model.pkl"

@st.cache_data(ttl=3600)
def load_all_data():
    tables = {}
    files = ['dim_users', 'dim_levels', 'fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']
    for f in files:
        path = os.path.join(DATA_PATH, f"{f}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Ép kiểu datetime cho các cột quan trọng
            for col in ['install_date', 'start_time', 'timestamp']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            tables[f] = df
        else:
            tables[f] = pd.DataFrame()
    return tables

def apply_filters(tables, countries, platforms, date_range, versions=None):
    """
    Hàm lọc dữ liệu đa năng: Sửa lỗi TypeError bằng cách kiểm tra kiểu dữ liệu của date_range.
    """
    u = tables['dim_users']
    if u.empty: return tables

    # 1. Khởi tạo mask lọc cho dim_users
    mask = u['country'].isin(countries) & u['platform'].isin(platforms)
    
    # 2. Chỉ lọc theo ngày nếu date_range là tuple/list có 2 phần tử ngày
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        try:
            start_date, end_date = date_range
            mask &= (u['install_date'].dt.date >= start_date) & (u['install_date'].dt.date <= end_date)
        except Exception:
            pass # Bỏ qua nếu không phải định dạng ngày

    u_filtered = u[mask]
    u_ids = u_filtered['user_id'].unique()
    
    filtered_tables = {'dim_users': u_filtered, 'dim_levels': tables['dim_levels']}
    
    # 3. Lọc các bảng fact
    for k in ['fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']:
        df = tables[k]
        f_df = df[df['user_id'].isin(u_ids)]
        
        # Lọc theo phiên bản nếu được cung cấp
        if versions and 'app_version' in f_df.columns:
            f_df = f_df[f_df['app_version'].isin(versions)]
            
        filtered_tables[k] = f_df
        
    return filtered_tables

def get_full_cohort_matrix(df_sessions, df_users):
    """Tạo bảng Cohort."""
    if df_sessions.empty or df_users.empty: return pd.DataFrame()
    df = pd.merge(df_sessions[['user_id', 'start_time']], df_users[['user_id', 'install_date']], on='user_id')
    df['day_diff'] = (df['start_time'].dt.date - df['install_date'].dt.date).apply(lambda x: x.days)
    df = df[(df['day_diff'] >= 0) & (df['day_diff'] <= 7)]
    
    cohort_sizes = df_users.groupby('install_date')['user_id'].nunique().reset_index()
    cohort_sizes.columns = ['Date', 'Total Users']
    
    matrix = df.groupby(['install_date', 'day_diff'])['user_id'].nunique().unstack(fill_value=0)
    retention_matrix = matrix.divide(matrix[0], axis=0)
    
    result = cohort_sizes.set_index('Date').join(retention_matrix)
    result.index = result.index.strftime('%d %b')
    return result
