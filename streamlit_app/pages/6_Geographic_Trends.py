import sys
from pathlib import Path
import streamlit as st
from datetime import date

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Geographic Trends", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
df_users = raw_data.get('dim_users')

if df_users is not None and not df_users.empty:
    st.title("Geographic User Distribution")
    
    # TÍNH TỔNG SỐ USER
    total_unique_users = df_users['user_id'].nunique()
    st.markdown(f"**Total Unique Users:** {total_unique_users:,}") # Hiển thị tổng số user

    # VẼ BẢN ĐỒ
    # Gọi hàm vẽ bản đồ từ chart_factory
    fig_map = chart_factory.plot_geo_choropleth(df_users)
    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.error("Không tìm thấy dữ liệu người dùng (dim_users.csv).")
