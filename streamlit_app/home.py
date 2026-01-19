import streamlit as st

st.set_page_config(page_title="Mobile Game Analytics", layout="wide")

# Custom CSS cho giao diện
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; }
</style>
""", unsafe_allow_html=True)

st.title("Mobile Game Analytics")
st.sidebar.title("Navigation")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Project Overview
    Dự án mô phỏng hệ thống **Real-time ELT Pipeline** cho Game di động 10 quốc gia.
    - **Tech Stack:** Python (Faker), BigQuery (UNNEST JSON), Streamlit.
    - **Key Insights:** Phân tích điểm gãy (Churn) dựa trên cấu hình thiết bị và độ khó màn chơi.
    """)
    st.info("Tip: Sử dụng menu bên trái để xem chi tiết từng khía cạnh sản phẩm.")

with col2:
    st.image("https://img.icons8.com/clouds/200/analytics.png")