import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

import data_utils, config, chart_factory

st.set_page_config(page_title="Predictive", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    st.title("Predictive Analytics")

    # 1. DIAGNOSTIC WITH DATA LABELS
    st.header("Diagnostic: Why Users Quit?")
    l3_events = raw_data['fact_gameplay_events'][raw_data['fact_gameplay_events']['level_id'] == 3]
    fail_reasons = l3_events[l3_events['event_name'] == 'level_fail']['fail_reason'].value_counts().reset_index()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        # Pie Chart có Label + Percent
        fig_pie = px.pie(fail_reasons, values='count', names='fail_reason', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label') # Data Label
        st.plotly_chart(chart_factory.styled_fig(fig_pie), use_container_width=True)
    with c2:
        st.warning("**Diagnostic:** 80% người chơi fail tại Level 3 do hết giờ. Cần nới lỏng timer.")

    st.divider()
    st.header("Churn Risk Forecast")
    
    predict_df = raw_data['fact_technical_health'].groupby('user_id').agg({'is_crash':'sum', 'fps_avg':'mean'}).reset_index()
    max_lvl = raw_data['fact_gameplay_events'].groupby('user_id')['level_id'].max().reset_index()
    predict_df = predict_df.merge(max_lvl, on='user_id')
    
    predict_df['churn_prob'] = predict_df.apply(lambda r: data_utils.predict_churn(r['is_crash'], r['fps_avg'], r['level_id']), axis=1)

    fig = px.scatter(predict_df, x="fps_avg", y="churn_prob", color="is_crash", 
                     title="Churn Probability vs FPS", color_continuous_scale="RdBu_r")
    st.plotly_chart(chart_factory.styled_fig(fig), use_container_width=True)
