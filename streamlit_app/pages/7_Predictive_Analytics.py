import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Predictive", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()
if not raw_data['dim_users'].empty:
    st.title("Predictive & Diagnostic Insights")

    st.header("Diagnostic: Why Level 3 Fails?")
    l3_data = raw_data['fact_gameplay_events'][raw_data['fact_gameplay_events']['level_id'] == 3]
    fail_df = l3_data[l3_data['event_name'] == 'level_fail']['fail_reason'].value_counts().reset_index()
    fig = px.pie(fail_df, values='count', names='fail_reason', hole=0.4, title="Level 3 Failure Reasons")
    st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)

    st.divider()
    st.header("Predictive: Churn Risk Forecast")
    # Giả lập churn dựa trên crash & fps
    risk_df = raw_data['fact_technical_health'].groupby('user_id').agg({'is_crash':'sum', 'fps_avg':'mean'}).reset_index()
    risk_df['churn_prob'] = risk_df['is_crash'].apply(lambda x: 0.8 if x > 2 else 0.1)
    
    fig_s = px.scatter(risk_df, x="fps_avg", y="churn_prob", color="is_crash", title="Churn Probability vs Technical Performance")
    st.plotly_chart(chart_factory.styled_fig(fig_s), use_container_width=True)
