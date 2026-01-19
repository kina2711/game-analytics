import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config

def draw_metric(label, value, sub_text=""):
    st.markdown(f"""
        <div class="glass-card">
            <small style="color: #6c757d; font-weight: 500;">{label}</small>
            <h2 style="margin: 5px 0; color: {config.COLORS['primary']}; font-size: 28px;">{value}</h2>
            <p style="color: #adb5bd; margin: 0; font-size: 12px;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

def styled_fig(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=config.COLORS['text'],
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def plot_gauge(value, title, target=0.25):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 18, 'color': config.COLORS['text']}},
        number = {'suffix': "", 'valueformat': ".1%", 'font': {'color': config.COLORS['primary']}},
        gauge = {
            'axis': {'range': [0, 0.5], 'tickformat': ".0%", 'tickcolor': config.COLORS['secondary']},
            'bar': {'color': config.COLORS['primary']},
            'bgcolor': "#f8f9fa",
            'threshold': {
                'line': {'color': config.COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))
    return styled_fig(fig)

def display_cohort_style(df):
    if df.empty: return
    days = [i for i in range(8) if i in df.columns]
    format_dict = {day: '{:.1%}' for day in days}
    format_dict['Total Users'] = '{:,}'

    styled_df = df.style.background_gradient(
        cmap='Blues', 
        subset=days,
        vmin=0, vmax=0.4
    ).format(format_dict)
    st.dataframe(styled_df, use_container_width=True)
