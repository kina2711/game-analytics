import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
    
    # Xác định các cột Day 0 -> Day 7 để tô màu
    days_cols = [c for c in df.columns if 'Day' in c]
    
    format_dict = {col: '{:.1%}' for col in days_cols}
    format_dict['Total Users'] = '{:,}'
    
    try:
        styled_df = df.style.background_gradient(
            cmap='Blues', 
            subset=days_cols, 
            vmin=0, vmax=0.4
        ).format(format_dict)
        
        # use_container_width=True -> Co giãn full màn hình
        st.dataframe(styled_df, use_container_width=True, height=400)
    except:
        st.dataframe(df.style.format(format_dict), use_container_width=True)

def display_funnel_table(df):
    st.dataframe(
        df,
        column_config={
            "Step": st.column_config.TextColumn("Step Name"),
            "Users": st.column_config.NumberColumn("Total Users", format="%d"),
            "Churn Rate": st.column_config.NumberColumn("Churn Rate", format="%.2f%%"),
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

def plot_geo_choropleth(df_users):
    if df_users.empty: return go.Figure()
    country_counts = df_users.groupby('country')['user_id'].nunique().reset_index()
    country_counts.columns = ['country', 'user_count']

    fig = px.choropleth(
        country_counts,
        locations="country",
        locationmode='ISO-3',
        color="user_count",
        hover_name="country",
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'user_count': 'Unique Users'},
        title='Users (group by country)'
    )
    fig.update_geos(showframe=False, showcoastlines=False, projection_type='equirectangular', visible=True, showcountries=True, countrycolor="#f0f0f0", showland=True, landcolor="white", showocean=False)
    return styled_fig(fig)
