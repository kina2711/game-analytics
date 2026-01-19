import pandas as pd
import streamlit as st
import os
import joblib

# CẤU HÌNH ĐƯỜNG DẪN
DATA_PATH = "data"
MODEL_PATH = "models/churn_model.pkl"

@st.cache_data(ttl=3600)
def load_all_data():
    """
    Đọc toàn bộ các file CSV từ thư mục data và chuẩn hóa định dạng thời gian.
    """
    tables = {}
    files = [
        'dim_users', 'dim_levels', 'fact_sessions',
        'fact_gameplay_events', 'fact_monetization', 'fact_technical_health'
    ]

    for f in files:
        path = os.path.join(DATA_PATH, f"{f}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Chuẩn hóa các cột thời gian để đảm bảo biểu đồ vẽ đúng
            for col in ['install_date', 'start_time', 'end_time', 'timestamp']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            tables[f] = df
        else:
            st.error(f"Không tìm thấy file dữ liệu: {path}")
            tables[f] = pd.DataFrame()

    return tables

def apply_filters(tables, countries, platforms, versions):
    """
    Logic lọc dữ liệu dùng chung (Centralized Filters) cho toàn bộ Dashboard.
    Đảm bảo tính nhất quán giữa các trang báo cáo.
    """
    # 1. Lọc bảng danh mục người dùng trước
    u = tables['dim_users']
    mask = u['country'].isin(countries) & u['platform'].isin(platforms)
    u_filtered = u[mask]

    # 2. Lấy danh sách ID người dùng đã lọc để áp dụng cho các bảng Fact
    u_ids = u_filtered['user_id'].unique()
    filtered_tables = {'dim_users': u_filtered, 'dim_levels': tables['dim_levels']}

    fact_keys = ['fact_sessions', 'fact_gameplay_events', 'fact_monetization', 'fact_technical_health']

    for k in fact_keys:
        df = tables[k]
        # Lọc theo User ID
        f_df = df[df['user_id'].isin(u_ids)]

        # Lọc theo App Version nếu có (thường dùng cho fact_sessions)
        if 'app_version' in f_df.columns and versions:
            f_df = f_df[f_df['app_version'].isin(versions)]

        filtered_tables[k] = f_df

    return filtered_tables

def get_retention_matrix(df_sessions, df_users):
    """
    Tính toán ma trận Cohort Retention (D0 - D30).
    """
    if df_sessions.empty or df_users.empty:
        return pd.DataFrame()

    # Merge để lấy ngày cài đặt gốc của mỗi user
    df = pd.merge(df_sessions, df_users[['user_id', 'install_date']], on='user_id')

    # Tính khoảng cách ngày kể từ khi cài đặt
    df['day_diff'] = (df['start_time'].dt.date - df['install_date'].dt.date).dt.days

    # Tạo bảng pivot đếm số lượng user duy nhất mỗi ngày
    pivot = df.pivot_table(index='install_date', columns='day_diff', values='user_id', aggfunc='nunique')

    # Chuyển thành tỷ lệ % (Day 0 là 100%)
    retention_matrix = pivot.divide(pivot.iloc[:, 0], axis=0)
    return retention_matrix

def predict_churn(is_crash, fps_avg, level_id):
    """
    Sử dụng mô hình ML Random Forest để dự báo xác suất Churn (Predictive Analysis).
    """
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            # Dữ liệu đầu vào phải khớp hoàn toàn với lúc train (is_crash, fps_avg, level_id)
            features = pd.DataFrame([[is_crash, fps_avg, level_id]],
                                    columns=['is_crash', 'fps_avg', 'level_id'])

            # Trả về xác suất thuộc nhóm Churned (Class 1)
            probability = model.predict_proba(features)[0][1]
            return probability
        except Exception as e:
            return None
    return None

def get_diagnostic_stats(df_gameplay):
    """
    Tổng hợp các chỉ số chẩn đoán (Diagnostic Analytics) về lỗi chơi game.
    """
    if df_gameplay.empty:
        return {"total_fails": 0, "top_reason": "N/A"}

    fails = df_gameplay[df_gameplay['event_name'] == 'level_fail']
    total_fails = len(fails)
    top_reason = fails['fail_reason'].value_counts().idxmax() if not fails.empty else "None"

    return {
        "total_fails": total_fails,
        "top_reason": top_reason
    }
