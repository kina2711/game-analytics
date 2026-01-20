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
            for col in ['install_date', 'start_time', 'timestamp']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            tables[f] = df
        else:
            tables[f] = pd.DataFrame()
    return tables

def apply_filters(tables, countries, platforms, date_range, versions=None):
    u = tables['dim_users']
    if u.empty: return tables
    mask = u['country'].isin(countries) & u['platform'].isin(platforms)
    
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        mask &= (u['install_date'].dt.date >= start_date) & (u['install_date'].dt.date <= end_date)

    u_filtered = u[mask]
    u_ids = u_filtered['user_id'].unique()
    
    filtered_tables = {'dim_users': u_filtered, 'dim_levels': tables['dim_levels']}
    for k in ['fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']:
        df = tables[k]
        f_df = df[df['user_id'].isin(u_ids)]
        if versions and 'app_version' in f_df.columns:
            f_df = f_df[f_df['app_version'].isin(versions)]
        filtered_tables[k] = f_df
    return filtered_tables

def get_full_cohort_matrix(df_sessions, df_users):
    if df_sessions.empty or df_users.empty: return pd.DataFrame()
    df = pd.merge(df_sessions[['user_id', 'start_time']], df_users[['user_id', 'install_date']], on='user_id')
    df['day_diff'] = (df['start_time'].dt.date - df['install_date'].dt.date).apply(lambda x: x.days)
    df = df[(df['day_diff'] >= 0) & (df['day_diff'] <= 7)]
    
    sizes = df_users.groupby('install_date')['user_id'].nunique().reset_index()
    sizes.columns = ['Date', 'Total Users']
    
    matrix = df.groupby(['install_date', 'day_diff'])['user_id'].nunique().unstack(fill_value=0)
    retention = matrix.divide(matrix[0], axis=0)
    
    res = sizes.set_index('Date').join(retention)
    res.index = res.index.strftime('%d %b')
    return res

def get_funnel_data(df_gameplay):
    if df_gameplay.empty: return pd.DataFrame()
    
    # Đếm unique users hoàn thành mỗi level
    funnel = df_gameplay[df_gameplay['event_name'] == 'level_complete']\
            .groupby('level_id')['user_id'].nunique().reset_index()
    
    # Sắp xếp theo Level
    funnel = funnel.sort_values('level_id')
    
    for i in range(1, len(funnel)):
        if funnel.iloc[i, 1] > funnel.iloc[i-1, 1]:
            funnel.iloc[i, 1] = funnel.iloc[i-1, 1]
            
    return funnel
    
def predict_churn(is_crash, fps_avg, level_id):
    if os.path.exists(MODEL_PATH):
        try:
            # Nạp model Random Forest đã huấn luyện
            model = joblib.load(MODEL_PATH)
            features = pd.DataFrame([[is_crash, fps_avg, level_id]], 
                                   columns=['is_crash', 'fps_avg', 'level_id'])
            # Trả về xác suất người chơi rời bỏ
            return model.predict_proba(features)[0][1]
        except Exception:
            return None
    return None
