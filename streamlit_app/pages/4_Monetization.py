import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Monetization", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
if not raw_data['dim_users'].empty:
    st.sidebar.header("Filters")
    sc = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:5])
    data = data_utils.apply_filters(raw_data, sc, ["iOS", "Android"], None)

    st.title("Monetization Analytics")
    
    c1, c2, c3 = st.columns(3)
    p_users = data['fact_monetization'][data['fact_monetization']['rev_type'] == 'IAP']['user_id'].nunique()
    total_rev = data['fact_monetization']['amount_usd'].sum()
    
    with c1: chart_factory.draw_metric("ARPPU", f"${total_rev/p_users:.2f}" if p_users > 0 else "$0")
    with c2: chart_factory.draw_metric("Conversion Rate", f"{(p_users/len(data['dim_users'])*100):.1f}%")
    with c3: chart_factory.draw_metric("Total Ad Revenue", f"${data['fact_monetization'][data['fact_monetization']['rev_type'] == 'Ads']['amount_usd'].sum():,.0f}")

    st.subheader("Revenue by Ad Format")
    ad_df = data['fact_monetization'][data['fact_monetization']['rev_type'] == 'Ads'].groupby('ad_format')['amount_usd'].sum().reset_index()
    fig = px.pie(ad_df, values='amount_usd', names='ad_format', hole=0.5, color_discrete_sequence=px.colors.sequential.RdPu)
    st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)
