import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Geographic Trends", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
if not raw_data['dim_users'].empty:
    st.title("Geographic Trends")

    iso_mapping = {'VN': 'VNM', 'US': 'USA', 'TH': 'THA', 'ID': 'IDN', 'PH': 'PHL', 'MY': 'MYS', 'SG': 'SGP', 'KR': 'KOR', 'JP': 'JPN', 'TW': 'TWN'}
    geo_data = raw_data['dim_users'].groupby('country')['user_id'].nunique().reset_index()
    geo_data['iso_alpha'] = geo_data['country'].map(iso_mapping)

    fig = px.choropleth(geo_data, locations="iso_alpha", color="user_id", hover_name="country", color_continuous_scale=[[0, "#161b22"], [1, config.COLORS['primary']]])
    st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)
