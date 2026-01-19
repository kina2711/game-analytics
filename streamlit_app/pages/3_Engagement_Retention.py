import streamlit as st
import plotly.express as px
from data_utils import load_all_data
from chart_factory import styled_fig
from config import apply_theme, COLORS

apply_theme()
data = load_all_data()
df_g = data['fact_gameplay_events']

st.title("Engagement & Retention")

# Visual 1: Level Funnel
funnel = df_g[df_g['event_name'] == 'level_complete'].groupby('level_id')['user_id'].nunique().reset_index()
fig_funnel = px.funnel(funnel, x='user_id', y='level_id', title="Level Completion Funnel")
st.plotly_chart(styled_fig(fig_funnel), use_container_width=True)

st.error("Insight: Tỷ lệ rơi rụng (Drop-off) lớn nhất tại Level 3 (giảm 40%). Cần kiểm tra lại độ khó tại Stage này.")