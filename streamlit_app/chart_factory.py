import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.colors as mcolors
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

def display_cohort_style(df_counts):
    if df_counts.empty: return

    # Tách cột Total Users và các cột Day
    day_cols = [c for c in df_counts.columns if 'Day' in c]
    
    # 1. Tính toán ma trận %
    # Chia số lượng từng ngày cho Total Users của dòng đó
    df_pct = df_counts[day_cols].div(df_counts['Total Users'], axis=0)
    
    # 2. Tạo ma trận text hiển thị (Dạng: "40.5% (123)")
    df_text = pd.DataFrame(index=df_counts.index, columns=df_counts.columns)
    
    # Format cột Total Users
    df_text['Total Users'] = df_counts['Total Users'].apply(lambda x: f"{x:,}")
    
    # Format các cột Day
    for col in day_cols:
        # Kết hợp % từ df_pct và số lượng từ df_counts
        # Sử dụng zip để iter qua từng dòng
        df_text[col] = [f"{p:.1%} ({c})" if c > 0 else "" 
                        for p, c in zip(df_pct[col], df_counts[col])]

    def style_gradient(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        cmap = mcolors.LinearSegmentedColormap.from_list("custom_blues", ["#ffffff", "#007bff"])
        
        for col in day_cols:
            # Lấy max value để normalize
            # Lấy cố định max=0.5 (50%) để màu đậm rõ hơn với retention thấp
            vmax = 0.5 
            
            for idx in data.index:
                val = df_pct.loc[idx, col] # Lấy giá trị % thực tế
                if pd.isna(val) or val == 0:
                    bg_color = "#ffffff"
                    text_color = "#000000"
                else:
                    # Normalize value 0 -> 1 cho colormap
                    norm_val = min(val / vmax, 1.0)
                    rgba = cmap(norm_val)
                    bg_color = mcolors.to_hex(rgba)
                    
                    # Chỉnh màu chữ trắng nếu nền quá đậm
                    text_color = "#ffffff" if norm_val > 0.6 else "#000000"
                
                styles.loc[idx, col] = f'background-color: {bg_color}; color: {text_color}'
        
        return styles

    # 4. Render
    st.dataframe(
        df_text.style.apply(style_gradient, axis=None),
        use_container_width=True,
        height=500
    )

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
