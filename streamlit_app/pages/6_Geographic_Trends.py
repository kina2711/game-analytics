import streamlit as st
import plotly.express as px
import pandas as pd
from data_utils import load_all_data, apply_filters
from chart_factory import styled_fig, draw_metric
from config import apply_theme, COLORS

# Áp dụng giao diện Cyberpunk
apply_theme()

# Load dữ liệu
data = load_all_data()
df_u = data['dim_users']
df_m = data['fact_monetization']

st.title("Geographic Market Trends")

# --- Mapping ISO-2 sang ISO-3 để vẽ bản đồ Plotly ---
iso_mapping = {
    'VN': 'VNM', 'US': 'USA', 'TH': 'THA', 'ID': 'IDN', 'PH': 'PHL',
    'MY': 'MYS', 'SG': 'SGP', 'KR': 'KOR', 'JP': 'JPN', 'TW': 'TWN'
}

# 1. Xử lý dữ liệu bản đồ
geo_users = df_u.groupby('country')['user_id'].nunique().reset_index()
geo_rev = df_m.merge(df_u[['user_id', 'country']], on='user_id')
geo_rev = geo_rev.groupby('country')['amount_usd'].sum().reset_index()

# Merge và thêm mã ISO-3
geo_data = pd.merge(geo_users, geo_rev, on='country', how='left').fillna(0)
geo_data['iso_alpha'] = geo_data['country'].map(iso_mapping)

# UI Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Global User Distribution")
    fig_map = px.choropleth(
        geo_data,
        locations="iso_alpha",
        color="user_id",
        hover_name="country",
        projection="natural earth",
        color_continuous_scale=[[0, "#161b22"], [1, COLORS['primary']]],
    )
    st.plotly_chart(styled_fig(fig_map), use_container_width=True)

with col2:
    st.subheader("Top Markets")
    top_countries = geo_data.sort_values('amount_usd', ascending=False).head(5)
    for _, row in top_countries.iterrows():
        st.write(f"**{row['country']}**")
        st.caption(f"Revenue: ${row['amount_usd']:,.0f}")
        st.progress(row['amount_usd'] / geo_data['amount_usd'].max())

# Chi tiết doanh thu theo khu vực
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.write("### User Count by Platform")
    fig_pie = px.sunburst(
        df_u, path=['country', 'platform'], values='user_id',
        color_discrete_sequence=px.colors.sequential.Cyan_r
    )
    st.plotly_chart(styled_fig(fig_pie), use_container_width=True)

with c2:
    st.write("### ARPU by Country")
    # Tính ARPU: Doanh thu / Số user từng nước
    geo_data['arpu'] = geo_data['amount_usd'] / geo_data['user_id']
    fig_arpu = px.bar(
        geo_data.sort_values('arpu', ascending=False),
        x='country', y='arpu',
        title="Average Revenue Per User by Country",
        color_discrete_sequence=[COLORS['secondary']]
    )
    st.plotly_chart(styled_fig(fig_arpu), use_container_width=True)

st.info("**Deduction:** Thị trường **US** và **KR** có ARPU cao nhất dù lượng user ít hơn **VN**, cho thấy tiềm năng khai thác doanh thu từ nhóm người dùng Tier-1.")