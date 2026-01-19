import sys
from pathlib import Path
import streamlit as st
from datetime import date

# Thêm đường dẫn để nhận diện module
utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

import data_utils
import chart_factory
import config

st.set_page_config(page_title="Engagement & Retention", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()

# SIDEBAR FILTERS
st.sidebar.header("Global Filters")
date_range = st.sidebar.date_input(
    "Install Date Range",
    value=(date(2025, 11, 1), date(2025, 11, 30)),
    min_value=date(2025, 1, 1),
    max_value=date(2026, 1, 31)
)

countries = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:3])
platforms = st.sidebar.multiselect("Platform", ["iOS", "Android"], ["iOS", "Android"])

if len(date_range) == 2:
    # Áp dụng filter
    data = data_utils.apply_filters(raw_data, countries, platforms, date_range)
    
    st.title("Engagement & Retention")
    
    # 1. COHORT TABLE
    st.subheader("User Retention Matrix (D0 - D7)")
    cohort_matrix = data_utils.get_full_cohort_matrix(data['fact_sessions'], data['dim_users'])
    
    if not cohort_matrix.empty:
        chart_factory.display_cohort_style(cohort_matrix)
    else:
        st.warning("No data found for the selected range.")

    # 2. FUNNEL (DIAGNOSTIC)
    st.divider()
    st.subheader("Level Completion Funnel")
    funnel = data['fact_gameplay_events'][data['fact_gameplay_events']['event_name'] == 'level_complete'].groupby('level_id')['user_id'].nunique().reset_index()
    import plotly.express as px
    fig_f = px.funnel(funnel, x='user_id', y='level_id', color_discrete_sequence=[config.COLORS['primary']])
    st.plotly_chart(chart_factory.styled_fig(fig_f), use_container_width=True)
