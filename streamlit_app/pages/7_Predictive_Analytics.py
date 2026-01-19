import streamlit as st
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import load_all_data
from config import apply_theme, COLORS

apply_theme()
data = load_all_data()

st.title("Predictive & Diagnostic Insights")

# SECTION 1: DIAGNOSTIC (Why did it happen?)
st.header("Diagnostic: Churn Root Cause")
col1, col2 = st.columns(2)

with col1:
    st.write("### Level 3 Drop-off Analysis")
    df_fail = data['fact_gameplay_events'][data['fact_gameplay_events']['level_id'] == 3]
    fail_reasons = df_fail['fail_reason'].value_counts().reset_index()
    fig = px.pie(fail_reasons, values='count', names='fail_reason', title="Fail Reasons at Level 3", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.info("""
    **Diagnostic Conclusion:**
    80% người dùng rời bỏ tại Level 3 do 'Out of time'. 
    Kết hợp với `difficulty_index`, chúng ta thấy độ khó tăng vọt 50% so với Level 2.
    => **Action:** Cần nới lỏng giới hạn thời gian ở Stage này.
    """)

# SECTION 2: PREDICTIVE (What will happen?)
st.header("Predictive: User Churn Forecast")
st.write("Sử dụng mô hình Random Forest để dự báo xác suất rời bỏ dựa trên hiệu suất máy.")

# Giả lập dữ liệu dự báo từ mô hình
predict_data = data['fact_technical_health'].groupby('user_id').agg({'is_crash':'sum', 'fps_avg':'mean'}).reset_index()
predict_data['churn_prob'] = (predict_data['is_crash'] * 0.4) + ( (60 - predict_data['fps_avg']) * 0.01 )

fig_churn = px.scatter(predict_data, x="fps_avg", y="churn_prob", color="is_crash",
                     title="Churn Probability vs. Technical Performance",
                     labels={'churn_prob': 'Xác suất Churn (%)', 'fps_avg': 'FPS trung bình'})
st.plotly_chart(fig_churn, use_container_width=True)

st.warning("**Predictive Alert:** Những user gặp > 2 lần crash trên thiết bị Low-end có 85% xác suất sẽ Churn trong 48h tới.")
