import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="User Acquisition", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
if not raw_data['dim_users'].empty:
    st.sidebar.header("Filters")
    sc = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:5])
    sp = st.sidebar.multiselect("Platform", ["iOS", "Android"], ["iOS", "Android"])
    data = data_utils.apply_filters(raw_data, sc, sp, None)

    st.title("User Acquisition & Growth")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: chart_factory.draw_metric("Total Spend", "$15,240", "Budget")
    with c2: chart_factory.draw_metric("Total Installs", f"{len(data['dim_users']):,}")
    with c3: chart_factory.draw_metric("Avg CPI", "$1.42", "-5%")
    with c4: 
        roas = (data['fact_monetization']['amount_usd'].sum() / 15240) * 100
        chart_factory.draw_metric("ROAS D7", f"{roas:.1f}%")

    l, r = st.columns(2)
    with l:
        st.subheader("Installs by Media Source")
        src_df = data['dim_users'].groupby('media_source')['user_id'].count().reset_index()
        fig = px.bar(src_df, x='media_source', y='user_id', color='media_source', color_discrete_map={'TikTok': config.COLORS['secondary'], 'Facebook': config.COLORS['primary'], 'Organic': config.COLORS['success']})
        st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)
    with r:
        st.subheader("Organic vs Non-Organic")
        org_df = data['dim_users']['media_source'].apply(lambda x: 'Organic' if x == 'Organic' else 'Paid').value_counts().reset_index()
        fig_p = px.pie(org_df, values='count', names='media_source', hole=0.5, color_discrete_sequence=[config.COLORS['primary'], config.COLORS['warning']])
        st.plotly_chart(chart_factory.styled_fig(fig_p), use_container_width=True)
