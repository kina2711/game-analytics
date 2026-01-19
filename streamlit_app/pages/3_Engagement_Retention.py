import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Retention", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
if not raw_data['dim_users'].empty:
    st.sidebar.header("Filters")
    sc = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:5])
    data = data_utils.apply_filters(raw_data, sc, ["iOS", "Android"], None)

    st.title("Engagement & Retention")
    
    st.subheader("User Retention Heatmap (Cohort Analysis)")
    matrix, sizes = data_utils.get_retention_matrix(data['fact_sessions'], data['dim_users'])
    if not matrix.empty:
        st.plotly_chart(chart_factory.plot_cohort_heatmap(matrix), use_container_width=True)

    st.divider()
    st.subheader("Gameplay Funnel (Level 1-10)")
    funnel = data['fact_gameplay_events'][data['fact_gameplay_events']['event_name'] == 'level_complete'].groupby('level_id')['user_id'].nunique().reset_index()
    fig_f = px.funnel(funnel, x='user_id', y='level_id', color_discrete_sequence=[config.COLORS['primary']])
    st.plotly_chart(chart_factory.styled_fig(fig_f), use_container_width=True)
