import pandas as pd
import streamlit as st
import os
import joblib

# Cấu hình đường dẫn
DATA_PATH = "data"
MODEL_PATH = "models/churn_model.pkl"

@st.cache_data(ttl=3600)
def load_all_data():
    """Đọc toàn bộ các file CSV và chuẩn hóa định dạng thời gian."""
    tables = {}
    files = [
        'dim_users', 'dim_levels', 'fact_sessions', 
        'fact_gameplay_events', 'fact_monetization', 'fact_technical_health'
    ]
    
    for f in files:
        path = os.path.join(DATA_PATH, f"{f}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Convert các cột thời gian
            for col in ['install_date', 'start_time', 'end_time', 'timestamp']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            tables[f] = df
        else:
            tables[f] = pd.DataFrame()
            
    return tables

def apply_filters(tables, countries, platforms, versions):
    """
    Hàm lọc dữ liệu tập trung (Phải có hàm này để fix lỗi AttributeError).
    """
    if tables['dim_users'].empty:
        return tables

    # 1. Lọc bảng dim_users
    u = tables['dim_users']
    mask = u['country'].isin(countries) & u['platform'].isin(platforms)
    u_filtered = u[mask]
    
    user_ids = u_filtered['user_id'].unique()
    filtered_tables = {'dim_users': u_filtered, 'dim_levels': tables['dim_levels']}
    
    # 2. Lọc các bảng Fact theo danh sách User ID
    fact_keys = ['fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']
    for k in fact_keys:
        df = tables[k]
        if df.empty:
            filtered_tables[k] = df
            continue
            
        f_df = df[df['user_id'].isin(user_ids)]
        
        # Lọc theo App Version nếu có
        if versions and 'app_version' in f_df.columns:
            f_df = f_df[f_df['app_version'].isin(versions)]
            
        filtered_tables[k] = f_df
        
    return filtered_tables

def get_retention_matrix(df_sessions, df_users):
    """Xây dựng ma trận Cohort Retention D0-D7 với ép kiểu dữ liệu an toàn."""
    if df_sessions.empty or df_users.empty: 
        return pd.DataFrame(), pd.Series()
    
    # 1. Tạo bản sao để tránh cảnh báo SettingWithCopy
    df_u = df_users[['user_id', 'install_date']].copy()
    df_s = df_sessions[['user_id', 'start_time']].copy()
    
    # 2. ÉP KIỂU LẦN CUỐI (Bắt buộc để fix lỗi .dt accessor)
    df_u['install_date'] = pd.to_datetime(df_u['install_date'], errors='coerce')
    df_s['start_time'] = pd.to_datetime(df_s['start_time'], errors='coerce')
    
    # 3. Loại bỏ dòng rỗng sau khi ép kiểu
    df_u = df_u.dropna(subset=['install_date'])
    df_s = df_s.dropna(subset=['start_time'])
    
    # 4. Merge dữ liệu
    df = pd.merge(df_s, df_u, on='user_id')
    
    # 5. Tính toán Day Diff
    # Sử dụng .dt.date để chuẩn hóa về ngày, sau đó trừ nhau
    df['day_diff'] = (df['start_time'].dt.date - df['install_date'].dt.date).apply(lambda x: x.days)
    
    # 6. Chỉ lấy từ Day 0 đến Day 30
    df = df[(df['day_diff'] >= 0) & (df['day_diff'] <= 30)]
    
    # 7. Tạo bảng Pivot
    cohort_pivot = df.pivot_table(index='install_date', columns='day_diff', values='user_id', aggfunc='nunique')
    
    if cohort_pivot.empty:
        return pd.DataFrame(), pd.Series()

    # 8. Tính tỷ lệ % Retention
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0)
    
    return retention_matrix, cohort_size

def predict_churn(is_crash, fps_avg, level_id):
    """Dự báo xác suất Churn sử dụng Machine Learning."""
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            features = pd.DataFrame([[is_crash, fps_avg, level_id]], 
                                   columns=['is_crash', 'fps_avg', 'level_id'])
            probability = model.predict_proba(features)[0][1]
            return probability
        except:
            return None
    return None

def get_diagnostic_stats(df_gameplay):
    """Phân tích chẩn đoán lỗi chơi game."""
    if df_gameplay.empty:
        return {"total_fails": 0, "top_reason": "N/A"}
        
    fails = df_gameplay[df_gameplay['event_name'] == 'level_fail']
    if fails.empty:
        return {"total_fails": 0, "top_reason": "None"}
        
    return {
        "total_fails": len(fails),
        "top_reason": fails['fail_reason'].value_counts().idxmax()
    }
