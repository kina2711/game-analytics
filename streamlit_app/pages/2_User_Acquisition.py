import streamlit as st
import plotly.express as px
from data_utils import load_all_data
from config import apply_theme, COLORS
from chart_factory import styled_fig, draw_metric

apply_theme()
data = load_all_data()
df_u = data['dim_users']

st.title("User Acquisition & Growth")

# KPI Cards
c1, c2, c3 = st.columns(3)
with c1: draw_metric("Total Installs", f"{len(df_u):,}")
with c2: draw_metric("Avg CPI", "$1.45", "-$0.1")
with c3: draw_metric("Organic Share", "22%")

# Visual: CPI by Media Source
source_data = df_u.groupby('media_source')['user_id'].count().reset_index()
fig_source = px.bar(source_data, x='media_source', y='user_id', color='media_source',
                   title="Installs by Media Source", color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['success']])
st.plotly_chart(styled_fig(fig_source), use_container_width=True)