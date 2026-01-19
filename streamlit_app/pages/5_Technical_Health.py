import streamlit as st
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import load_all_data
from chart_factory import styled_fig
from config import apply_theme, COLORS

apply_theme()
data = load_all_data()
df_h = data['fact_technical_health']

st.title("Technical Health & Performance")

# Visual 1: FPS Distribution
fig_fps = px.histogram(df_h, x="fps_avg", nbins=20, title="FPS Distribution Across Devices",
                      color_discrete_sequence=[COLORS['success']])
st.plotly_chart(styled_fig(fig_fps), use_container_width=True)

# Visual 2: Crash Rate by Device Tier
crash_tier = df_h.groupby('device_tier')['is_crash'].mean().reset_index()
fig_crash = px.bar(crash_tier, x='device_tier', y='is_crash', title="Crash Rate by Device Tier",
                  color_discrete_sequence=[COLORS['danger']])
st.plotly_chart(styled_fig(fig_crash), use_container_width=True)

st.warning("Cảnh báo: Thiết bị Low-end có tỷ lệ Crash cao đột biến. Kiến nghị Team Dev kiểm tra lại Memory Leak tại Stage 5.")
