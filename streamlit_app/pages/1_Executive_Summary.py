import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

# 1. MASTER IMPORT FIX (Phải đặt ở đầu file)
# Tự động tìm thư mục 'streamlit_app' để nạp data_utils, config...
utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

try:
    import data_utils
    import config
    import chart_factory
except ImportError as e:
    st.error(f"Không thể nạp module hỗ trợ: {e}")
    st.stop()

# 2. CẤU HÌNH TRANG
st.set_page_config(page_title="Executive Overview", layout="wide")
config.apply_theme()

# 3. LOAD VÀ FILTER DATA
raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    # Sidebar: Bộ lọc toàn cục (Slicers)
    st.sidebar.header("Dashboard Filters")
    
    selected_countries = st.sidebar.multiselect(
        "Select Country", 
        options=raw_data['dim_users']['country'].unique(),
        default=raw_data['dim_users']['country'].unique()[:5]
    )
    
    selected_platforms = st.sidebar.multiselect(
        "Platform", 
        options=["iOS", "Android"], 
        default=["iOS", "Android"]
    )
    
    selected_versions = st.sidebar.multiselect(
        "App Version", 
        options=raw_data['fact_sessions']['app_version'].unique(),
        default=raw_data['fact_sessions']['app_version'].unique()
    )

    # Áp dụng logic lọc tập trung
    data = data_utils.apply_filters(raw_data, selected_countries, selected_platforms, selected_versions)

    # 4. GIAO DIỆN CHÍNH
    st.title("Executive Overview")
    st.markdown("Cái nhìn 360 độ về sức khỏe vận hành và doanh thu của trò chơi.")

    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_rev = data['fact_monetization']['amount_usd'].sum()
        chart_factory.draw_metric("Total Revenue", f"${total_rev:,.0f}", "+12%")
        
    with col2:
        dau = data['fact_sessions']['user_id'].nunique()
        chart_factory.draw_metric("Daily Active Users", f"{dau:,}")
        
    with col3:
        new_users = data['dim_users']['user_id'].nunique()
        chart_factory.draw_metric("New Installs", f"{new_users:,}")
        
    with col4:
        arpdau = total_rev / dau if dau > 0 else 0
        chart_factory.draw_metric("ARPDAU", f"${arpdau:.2f}")
        
    with col5:
        # Stickiness Ratio = DAU/MAU (Giả lập MAU là tổng user trong kỳ)
        mau = raw_data['fact_sessions']['user_id'].nunique()
        stickiness = (dau / mau) if mau > 0 else 0
        chart_factory.draw_metric("Stickiness", f"{stickiness:.1%}")

    # Visuals Row 1
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("DAU & Revenue Trend")
        # Kết hợp dữ liệu phiên chơi và doanh thu theo ngày
        daily_rev = data['fact_monetization'].groupby(data['fact_monetization']['timestamp'].dt.date)['amount_usd'].sum().reset_index()
        fig_rev = px.area(daily_rev, x='timestamp', y='amount_usd', 
                         title="Daily Gross Revenue Mix",
                         color_discrete_sequence=[config.COLORS['primary']])
        st.plotly_chart(chart_factory.styled_fig(fig_rev), use_container_width=True)

    with c_right:
        st.subheader("Stickiness Gauge")
        # Sử dụng Gauge chart để đo độ gắn kết
        fig_gauge = chart_factory.plot_gauge(stickiness, "User Stickiness", target=0.25)
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Visuals Row 2: Table & Distribution
    st.divider()
    t_left, t_right = st.columns(2)
    
    with t_left:
        st.subheader("Top 5 Countries by Revenue")
        geo_rev = data['fact_monetization'].merge(data['dim_users'][['user_id', 'country']], on='user_id')
        top_countries = geo_rev.groupby('country')['amount_usd'].sum().sort_values(ascending=False).head(5).reset_index()
        st.dataframe(top_countries, use_container_width=True)

    with t_right:
        st.subheader("Revenue Type Distribution")
        rev_dist = data['fact_monetization'].groupby('rev_type')['amount_usd'].sum().reset_index()
        fig_pie = px.pie(rev_dist, values='amount_usd', names='rev_type', 
                        hole=0.4, color_discrete_sequence=[config.COLORS['primary'], config.COLORS['secondary']])
        st.plotly_chart(chart_factory.styled_fig(fig_pie), use_container_width=True)

else:
    st.error("Không tìm thấy dữ liệu trong thư mục data/. Vui lòng chạy data_generator.py trước.")
