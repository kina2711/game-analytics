import sys
from pathlib import Path
import streamlit as st
from datetime import date
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

import data_utils, config, chart_factory

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
        
        c1, c2, c3, c4 = st.columns(4)
        total_rev = data['fact_monetization']['amount_usd'].sum()
        dau = data['fact_sessions']['user_id'].nunique()
        
        with c1: chart_factory.draw_metric("Total Revenue", f"${total_rev:,.0f}", "Gross")
        with c2: chart_factory.draw_metric("Unique Players (DAU)", f"{dau:,}", "Active Today")
        with c3:
            arpdau = total_rev / dau if dau > 0 else 0
            chart_factory.draw_metric("ARPDAU", f"${arpdau:.2f}", "Rev/User")
        with c4: chart_factory.draw_metric("New Installs", f"{len(data['dim_users']):,}", "Growth")

        st.divider()

        l_col, r_col = st.columns([2, 1])
        with l_col:
            st.subheader("Daily Revenue Trend")
            daily_rev = data['fact_monetization'].groupby(data['fact_monetization']['timestamp'].dt.date)['amount_usd'].sum().reset_index()
            # Thêm Data Label (text) cho biểu đồ Area
            fig = px.area(daily_rev, x='timestamp', y='amount_usd', text='amount_usd', color_discrete_sequence=[config.COLORS['primary']])
            fig.update_traces(texttemplate='%{text:.2s}', textposition='top center')
            st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)
            
        with r_col:
            st.subheader("User Stickiness")
            stickiness = (dau / raw_data['dim_users']['user_id'].nunique()) if not raw_data['dim_users'].empty else 0
            st.plotly_chart(chart_factory.plot_gauge(stickiness, "DAU/MAU Ratio", target=0.7), use_container_width=True)

        st.subheader("Top 5 Countries by Revenue")
        geo_rev = data['fact_monetization'].merge(data['dim_users'][['user_id', 'country']], on='user_id')
        top_5 = geo_rev.groupby('country')['amount_usd'].sum().sort_values(ascending=False).head(5).reset_index()
        
        fig_bar = px.bar(top_5, x='amount_usd', y='country', orientation='h', text='amount_usd', color='amount_usd', color_continuous_scale='Blues')
        fig_bar.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(chart_factory.styled_fig(fig_bar), use_container_width=True)
else:
    st.error("Vui lòng kiểm tra dữ liệu.")
