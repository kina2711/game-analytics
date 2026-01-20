import streamlit as st
import pandas as pd
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

def plot_gauge(value, title, target=0.25):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value * 100,
        title = {'text': title, 'font': {'size': 16, 'color': config.COLORS['text']}},
        number = {'suffix': "%", 'valueformat': ".1%", 'font': {'color': config.COLORS['primary']}},
        gauge = {
            'axis': {'range': [0, 50], 'tickformat': ".0%"},
            'bar': {'color': config.COLORS['primary']},
            'bgcolor': "#f8f9fa",
            'steps': [{'range': [0, 15], 'color': "#fff3f3"}, {'range': [15, 50], 'color': "#f3fff3"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': target * 100}
        }
    ))
    fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font_color=config.COLORS['text'])
    return fig

def display_cohort_style(df):
    if df.empty: return
    days = [i for i in range(8) if i in df.columns]
    format_dict = {day: '{:.1%}' for day in days}
    format_dict['Total Users'] = '{:,}'
    try:
        styled_df = df.style.background_gradient(cmap='Blues', subset=days, vmin=0, vmax=0.4).format(format_dict)
        st.dataframe(styled_df, use_container_width=True)
    except:
        st.dataframe(df.style.format(format_dict), use_container_width=True)

def display_funnel_table(df):
    st.dataframe(
        df,
        column_config={
            "Step": st.column_config.TextColumn("Step Name"),
            "Users": st.column_config.NumberColumn("Total Users", format="%d"),
            "Churn Rate": st.column_config.NumberColumn("Churn Rate", format="%.2f%%", help="Tỷ lệ rơi rụng"),
            "Total Completion": st.column_config.ProgressColumn("Total Completion", format="%.2f%%", min_value=0, max_value=1),
        },
        use_container_width=True,
        hide_index=True
    )

def styled_fig(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font_color=config.COLORS['text'],
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig
