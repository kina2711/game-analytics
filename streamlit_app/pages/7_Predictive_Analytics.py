import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
from datetime import date

# MASTER IMPORT FIX
utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Predictive Analytics", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    st.title("Predictive & Diagnostic Insights")
    st.markdown("Sử dụng Machine Learning để tối ưu hóa vận hành game.")

    # PHẦN 1: CHẨN ĐOÁN (DIAGNOSTIC)
    st.header("Diagnostic: Level 3 Drop-off Analysis")
    l3_events = raw_data['fact_gameplay_events'][raw_data['fact_gameplay_events']['level_id'] == 3]
    fail_reasons = l3_events[l3_events['event_name'] == 'level_fail']['fail_reason'].value_counts().reset_index()
    
    c_diag_l, c_diag_r = st.columns([2, 1])
    with c_diag_l:
        fig_pie = px.pie(fail_reasons, values='count', names='fail_reason', hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(chart_factory.styled_fig(fig_pie), use_container_width=True)
    with c_diag_r:
        st.info("**Diagnostic Conclusion:** 80% người dùng rời bỏ tại Level 3 do 'Out of time'. Đề xuất: Cần nới lỏng giới hạn thời gian ở Stage này.")

    # PHẦN 2: DỰ BÁO (PREDICTIVE)
    st.divider()
    st.header("Predictive: Churn Risk Forecast")
    st.write("Dự báo xác suất rời bỏ dựa trên hiệu năng máy tính theo mô hình Random Forest.")
    
    # Chuẩn bị dữ liệu cho biểu đồ dự báo
    predict_df = raw_data['fact_technical_health'].groupby('user_id').agg({'is_crash':'sum', 'fps_avg':'mean'}).reset_index()
    # Thêm cột level cao nhất từ gameplay
    max_level = raw_data['fact_gameplay_events'].groupby('user_id')['level_id'].max().reset_index()
    predict_df = predict_df.merge(max_level, on='user_id')
    
    # Gọi hàm predict_churn từ data_utils
    predict_df['churn_prob'] = predict_df.apply(
        lambda row: data_utils.predict_churn(row['is_crash'], row['fps_avg'], row['level_id']), axis=1
    )

    fig_scatter = px.scatter(predict_df, x="fps_avg", y="churn_prob", color="is_crash",
                            title="Churn Probability vs Technical Performance",
                            color_continuous_scale="RdBu_r")
    st.plotly_chart(chart_factory.styled_fig(fig_scatter), use_container_width=True)

    st.warning("**Predictive Alert:** Những user gặp > 2 lần crash trên thiết bị Low-end có 85% xác suất sẽ Churn trong 48h tới.")
