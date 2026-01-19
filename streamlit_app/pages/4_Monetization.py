import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_utils import load_all_data
from chart_factory import styled_fig, draw_metric
from config import apply_theme, COLORS

apply_theme()
data = load_all_data()
df_m = data['fact_monetization']
df_u = data['dim_users']

st.title("Monetization Deep-dive")

# KPI Cards
paying_users = df_m['user_id'].nunique()
total_users = df_u['user_id'].nunique()
conv_rate = (paying_users / total_users) * 100 if total_users > 0 else 0
total_rev = df_m['amount_usd'].sum()
arppu = total_rev / paying_users if paying_users > 0 else 0

c1, c2, c3 = st.columns(3)
with c1: draw_metric("ARPPU", f"${arppu:.2f}", "Whale-driven")
with c2: draw_metric("Conversion Rate", f"{conv_rate:.2f}%")
with c3:
    ad_rev = df_m[df_m['rev_type'] == 'Ads']['amount_usd'].sum()
    draw_metric("Total Ad Revenue", f"${ad_rev:,.0f}")

# Visual 1: Revenue by Ad Format (Donut Chart)
ad_data = df_m[df_m['rev_type'] == 'Ads'].groupby('ad_format')['amount_usd'].sum().reset_index()
fig_donut = px.pie(ad_data, values='amount_usd', names='ad_format', hole=.5,
                   title="Revenue by Ad Format", color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(styled_fig(fig_donut), use_container_width=True)

# Visual 2: Cumulative Revenue (Waterfall)
daily_rev = df_m.groupby(df_m['timestamp'].dt.date)['amount_usd'].sum().reset_index()
daily_rev['cumulative'] = daily_rev['amount_usd'].cumsum()
fig_waterfall = go.Figure(go.Waterfall(
    name = "Revenue", orientation = "v",
    x = daily_rev['timestamp'],
    y = daily_rev['amount_usd'],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
))
fig_waterfall.update_layout(title="Cumulative Monthly Revenue")
st.plotly_chart(styled_fig(fig_waterfall), use_container_width=True)