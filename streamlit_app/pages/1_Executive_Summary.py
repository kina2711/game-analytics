import sys
from pathlib import Path
import streamlit as st
from datetime import date
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Executive Overview", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    st.sidebar.header("Filters")
    dr = st.sidebar.date_input("Period", [date(2025, 11, 1), date(2025, 11, 30)])
    
    countries = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:5])
    platforms = st.sidebar.multiselect("Platform", ["iOS", "Android"], ["iOS", "Android"])

    if len(dr) == 2:
        data = data_utils.apply_filters(raw_data, countries, platforms, dr)

        st.title("Executive Overview")
        st.markdown("Báo cáo tổng quan về người chơi và doanh thu.")

        c1, c2, c3, c4 = st.columns(4)
        
        total_rev = data['fact_monetization']['amount_usd'].sum()
        unique_players = data['fact_sessions']['user_id'].nunique() # Unique Players (DAU)
        
        with c1:
            chart_factory.draw_metric("Total Revenue", f"${total_rev:,.0f}", "Gross")
        with c2:
            # Số người chơi unique (DAU)
            chart_factory.draw_metric("Unique Players (DAU)", f"{unique_players:,}", "Active")
        with c3:
            # Doanh thu chia cho số người chơi (ARPDAU)
            arpdau = total_rev / unique_players if unique_players > 0 else 0
            chart_factory.draw_metric("ARPDAU", f"${arpdau:.2f}", "Rev/Player")
        with c4:
            new_installs = len(data['dim_users'])
            chart_factory.draw_metric("New Installs", f"{new_installs:,}", "Growth")

        st.divider()

        # Visuals Row
        l_col, r_col = st.columns([2, 1])
        with l_col:
            st.subheader("Daily Revenue Trend")
            daily_rev = data['fact_monetization'].groupby(data['fact_monetization']['timestamp'].dt.date)['amount_usd'].sum().reset_index()
            fig_rev = px.line(daily_rev, x='timestamp', y='amount_usd', color_discrete_sequence=[config.COLORS['primary']])
            st.plotly_chart(chart_factory.styled_fig(fig_rev), use_container_width=True)
            
        with r_col:
            st.subheader("User Stickiness")
            # Gauge đo độ gắn kết (Đã fix AttributeError)
            stickiness = (unique_players / raw_data['dim_users']['user_id'].nunique()) if not raw_data['dim_users'].empty else 0
            fig_gauge = chart_factory.plot_gauge(stickiness, "DAU/MAU Ratio", target=0.20)
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Top 5 Countries Table (Theo image_25babc.png)
        st.subheader("Top 5 Countries by Revenue")
        geo_rev = data['fact_monetization'].merge(data['dim_users'][['user_id', 'country']], on='user_id')
        top_5 = geo_rev.groupby('country')['amount_usd'].sum().sort_values(ascending=False).head(5).reset_index()
        st.dataframe(top_5, use_container_width=True)

else:
    st.error("Vui lòng kiểm tra dữ liệu trong thư mục data/.")
