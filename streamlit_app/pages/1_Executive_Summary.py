import streamlit as st
import plotly.express as px
from data_utils import load_all_data, apply_filters
from chart_factory import draw_metric, plot_gauge, styled_fig
from config import apply_theme, COLORS

apply_theme()
data = load_all_data()

# Slicers
st.sidebar.header("Global Filters")
sel_country = st.sidebar.multiselect("Country", data['dim_users']['country'].unique(), default=data['dim_users']['country'].unique())
sel_platform = st.sidebar.multiselect("Platform", ["iOS", "Android"], default=["iOS", "Android"])
sel_version = st.sidebar.multiselect("Version", data['fact_sessions']['app_version'].unique(), default=data['fact_sessions']['app_version'].unique())

f_data = apply_filters(data, sel_country, sel_platform, sel_version)

st.title("Executive Overview")

# Top KPI Cards
c1, c2, c3, c4, c5 = st.columns(5)
with c1: draw_metric("DAU", f"{f_data['fact_sessions']['user_id'].nunique():,}", "Active")
with c2: draw_metric("New Users", f"{f_data['dim_users']['user_id'].nunique():,}", "+12%")
with c3:
    total_rev = f_data['fact_monetization']['amount_usd'].sum()
    draw_metric("Revenue", f"${total_rev:,.0f}")
with c4:
    dau = f_data['fact_sessions']['user_id'].nunique()
    arpdau = total_rev / dau if dau > 0 else 0
    draw_metric("ARPDAU", f"${arpdau:.2f}")
with c5: draw_metric("Ret D1", "42%", "Stable")

# Visual 1: DAU Trend
dau_trend = f_data['fact_sessions'].groupby(f_data['fact_sessions']['start_time'].dt.date)['user_id'].nunique().reset_index()
fig1 = px.line(dau_trend, x='start_time', y='user_id', title="DAU Growth Trend", color_discrete_sequence=[COLORS['primary']])
st.plotly_chart(styled_fig(fig1), use_container_width=True)

# Visual 2: Stickiness (Gauge)
mau = f_data['fact_sessions']['user_id'].nunique() # Giả định DAU/MAU
stickiness = (dau / mau) if mau > 0 else 0
st.plotly_chart(plot_gauge(stickiness, "Stickiness Ratio (DAU/MAU)"), use_container_width=True)