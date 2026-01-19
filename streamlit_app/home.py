import sys
from pathlib import Path
import streamlit as st

utils_path = str(Path(__file__).resolve().parent)
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

try:
    import config
    import data_utils
except ImportError as e:
    st.error(f"Lỗi nạp module tại Home: {e}")
    st.stop()

# CẤU HÌNH TRANG
st.set_page_config(page_title="Mobile Game Analytics | Rabbit", layout="wide")
config.apply_theme() # Giao diện sáng

# GIAO DIỆN CHÍNH
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Icon hoặc hình ảnh minh họa
    st.write("") 

with col_title:
    st.title("Mobile Game Analytics Dashboard")
    st.markdown(f"**Author:** Thái Trung Kiên (Rabbit) | Data Analyst")

st.divider()

# PHẦN 1: GIỚI THIỆU DỰ ÁN
st.header("Project Overview")
st.write("""
Dự án mô phỏng hệ thống **Real-time ELT Pipeline** cho Game di động vận hành trên 10 quốc gia. 
Hệ thống chuyển hóa dữ liệu thô thành các insight chiến lược giúp tối ưu hóa doanh thu và giữ chân người chơi.
""")

c1, c2 = st.columns(2)
with c1:
    st.info("""
    **Tech Stack:**
    - **Language:** Python (Pandas, Numpy)
    - **Visualization:** Streamlit, Plotly
    - **Machine Learning:** Scikit-learn (Joblib for Model Deployment)
    - **Database:** Supabase integration
    """)

with c2:
    st.success("""
    **Key Analytics:**
    - **Descriptive:** KPI tổng quan (DAU, ARPDAU, Revenue)
    - **Diagnostic:** Phân tích phễu Level (Drop-off points)
    - **Predictive:** Dự báo Churn dựa trên hiệu năng thiết bị (Random Forest)
    """)

# PHẦN 2: HƯỚNG DẪN ĐIỀU HƯỚNG
st.divider()
st.subheader("Navigation Guide")
st.markdown("""
Sử dụng menu bên trái để khám phá các khía cạnh khác nhau của sản phẩm:
1. **Executive Summary**: Các chỉ số sức khỏe game quan trọng nhất.
2. **Engagement & Retention**: Ma trận Cohort 7 ngày và Phễu người chơi.
3. **Monetization Deep-dive**: Phân tích hành vi nạp tiền và doanh thu Ads.
4. **Predictive Analytics**: Sử dụng AI để dự báo rủi ro người chơi rời bỏ.
""")
st.warning("**Tip:** Dataset được giả lập cho khoảng thời gian từ **01/11/2025 đến 30/11/2025**. Vui lòng chọn khoảng ngày này tại bộ lọc để xem dữ liệu đầy đủ nhất.")
