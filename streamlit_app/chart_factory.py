import streamlit as st
import pandas as pd
import plotly.express as px
import config

def draw_metric(label, value, sub_text=""):
    """Thẻ KPI."""
    st.markdown(f"""
        <div class="glass-card">
            <small style="color: #6c757d; font-weight: 500;">{label}</small>
            <h2 style="margin: 5px 0; color: {config.COLORS['primary']}; font-size: 28px;">{value}</h2>
            <p style="color: #adb5bd; margin: 0; font-size: 12px;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

def styled_fig(fig):
    """Chuẩn hóa biểu đồ Plotly."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=config.COLORS['text'],
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def display_cohort_style(df):
    """
    Vẽ bảng Cohort 7 ngày.
    """
    if df.empty:
        st.warning("Không có dữ liệu để hiển thị bảng Cohort.")
        return

    # Xác định các cột Day 0 đến Day 7 thực tế có trong data
    days = [i for i in range(8) if i in df.columns]
    
    # Thiết lập định dạng: % cho các cột Day, số nguyên cho Total Users
    format_dict = {day: '{:.1%}' for day in days}
    format_dict['Total Users'] = '{:,}'

    # Tạo dải màu gradient
    styled_df = df.style.background_gradient(
        cmap='Blues', 
        subset=days,
        vmin=0, vmax=0.4
    ).format(format_dict)

    st.dataframe(styled_df, use_container_width=True)
