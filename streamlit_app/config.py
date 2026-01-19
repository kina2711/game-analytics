import streamlit as st
import pandas as pd
import plotly.express as px
import config

def draw_metric(label, value, sub_text=""):
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px;">
            <p style="color: #aaa; margin: 0; font-size: 14px;">{label}</p>
            <h2 style="margin: 5px 0; color: #00d4ff; font-size: 32px;">{value}</h2>
            <p style="color: #555; margin: 0; font-size: 12px;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

def display_cohort_style(df):
    """Vẽ bảng Cohort có màu sắc gradient đúng mẫu."""
    # Chỉ định các cột Day 0 - Day 7
    days = [i for i in range(8) if i in df.columns]
    
    # Định dạng hiển thị
    format_dict = {day: '{:.1%}' for day in days}
    format_dict['Total Users'] = '{:,}'

    # Tạo style màu xanh
    styled_df = df.style.background_gradient(
        cmap='Blues', 
        subset=days,
        vmin=0, vmax=0.4
    ).format(format_dict)

    st.write(styled_df)

def styled_fig(fig):
    """Chuẩn hóa biểu đồ Plotly sang Dark Mode."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        template="plotly_dark"
    )
    return fig
