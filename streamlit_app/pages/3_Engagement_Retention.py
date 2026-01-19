import streamlit as st
from data_utils import load_all_data, get_retention_matrix
from chart_factory import plot_cohort_heatmap, styled_fig
import plotly.express as px
from config import apply_theme

apply_theme()
st.title("Engagement & Retention Analytics")

data = load_all_data()

# Phần 1: Ma trận Cohort
st.subheader("User Retention Matrix (Cohort Analysis)")
matrix, sizes = get_retention_matrix(data['fact_sessions'], data['dim_users'])

if not matrix.empty:
    st.plotly_chart(plot_cohort_heatmap(matrix), use_container_width=True)
    st.info("Tip: Hàng đầu tiên thể hiện nhóm user cũ nhất, cột Day 1 là tỷ lệ quay lại sau 24h.")
else:
    st.warning("Chưa có đủ dữ liệu để tạo ma trận Cohort.")

# Phần 2: Phễu Gameplay
st.divider()
st.subheader("Level Completion Funnel")
df_g = data['fact_gameplay_events']
funnel = df_g[df_g['event_name'] == 'level_complete'].groupby('level_id')['user_id'].nunique().reset_index()

fig_f = px.funnel(funnel, x='user_id', y='level_id', title="Drop-off từ Level 1 đến 10")
st.plotly_chart(styled_fig(fig_f), use_container_width=True)
