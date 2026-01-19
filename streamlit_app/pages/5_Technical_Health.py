import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Technical Health", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
if not raw_data['dim_users'].empty:
    data = data_utils.apply_filters(raw_data, raw_data['dim_users']['country'].unique(), ["iOS", "Android"], None)

    st.title("Technical Health")
    
    st.subheader("FPS Distribution by Device Tier")
    # Merge health với users để lấy device_tier
    df_h = data['fact_technical_health'].merge(data['dim_users'][['user_id', 'device_tier']], on='user_id')
    fig = px.histogram(df_h, x="fps_avg", color="device_tier", barmode="overlay", color_discrete_map={'High-end': config.COLORS['success'], 'Low-end': config.COLORS['danger'], 'Mid-range': config.COLORS['warning']})
    st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)

    st.divider()
    st.subheader("Crash Rate by Platform")
    crash_df = df_h.groupby('device_tier')['is_crash'].mean().reset_index()
    fig_b = px.bar(crash_df, x='device_tier', y='is_crash', title="Average Crash Rate", color_discrete_sequence=[config.COLORS['secondary']])
    st.plotly_chart(chart_factory.styled_fig(fig_b), use_container_width=True)
