import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import job_lib
import os

def train_model():
    # Load data
    users = pd.read_csv('data/dim_users.csv')
    health = pd.read_csv('data/fact_technical_health.csv')
    gameplay = pd.read_csv('data/fact_gameplay_events.csv')
    sessions = pd.read_csv('data/fact_sessions.csv')

    # 1. Feature Engineering: Tạo đặc trưng
    # - Số lần crash
    crash_counts = health.groupby('user_id')['is_crash'].sum().reset_index()
    # - FPS trung bình
    avg_fps = health.groupby('user_id')['fps_avg'].mean().reset_index()
    # - Level cao nhất đạt được
    max_level = gameplay.groupby('user_id')['level_id'].max().reset_index()

    # 2. Xác định Label (Churn): Không chơi quá 3 ngày kể từ khi cài đặt
    sessions['start_time'] = pd.to_datetime(sessions['start_time'])
    users['install_date'] = pd.to_datetime(users['install_date'])
    last_session = sessions.groupby('user_id')['start_time'].max().reset_index()

    df = users.merge(last_session, on='user_id').merge(crash_counts, on='user_id').merge(avg_fps, on='user_id').merge(
        max_level, on='user_id')
    df['days_active'] = (df['start_time'] - df['install_date']).dt.days
    df['is_churned'] = (df['days_active'] < 3).astype(int)

    # 3. Training
    features = ['is_crash', 'fps_avg', 'level_id']
    X = df[features]
    y = df['is_churned']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    print("Model trained. Feature Importance:", dict(zip(features, model.feature_importances_)))
    return model

if __name__ == "__main__":
    train_model()
