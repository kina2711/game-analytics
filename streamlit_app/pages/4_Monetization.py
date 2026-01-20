import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
from datetime import date

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

try:
    import data_utils, config, chart_factory
except ImportError: st.stop()

st.set_page_config(page_title="Monetization", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    # FILTERS
    st.sidebar.header("Monetization Filters")
    dr = st.sidebar.date_input("Period", [date(2025, 11, 1), date(2025, 11, 30)])
    countries = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:5])
    
    if len(dr) == 2:
        # Lọc dữ liệu
        data = data_utils.apply_filters(raw_data, countries, ["iOS", "Android"], dr)
        df_mon = data['fact_monetization']
        
        st.title("Monetization Deep-dive")
        
        # SECTION 1: TOP 3 KPIs
        # Tính toán cơ bản
        total_rev = df_mon['amount_usd'].sum()
        paying_users = df_mon['user_id'].nunique()
        arppu = total_rev / paying_users if paying_users > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        with c1: chart_factory.draw_metric("Total Revenue", f"${total_rev:,.0f}", "Gross Revenue")
        with c2: chart_factory.draw_metric("Paying Users", f"{paying_users:,}", "Converted Users")
        with c3: chart_factory.draw_metric("ARPPU", f"${arppu:.2f}", "Avg Rev per Paying User")
        
        st.divider()

        # SECTION 2: REVENUE TREND & DEEP DIVE METRICS
        # Layout: 70% Chart bên trái - 30% Chỉ số bên phải
        col_trend, col_metrics = st.columns([2.5, 1])
        
        with col_trend:
            st.subheader("Revenue Trend")
            if not df_mon.empty:
                daily_rev = df_mon.groupby(df_mon['timestamp'].dt.date)['amount_usd'].sum().reset_index()
                # Line Chart với Data Label
                fig_rev = px.line(daily_rev, x='timestamp', y='amount_usd', markers=True, 
                                  title="Daily Revenue", color_discrete_sequence=[config.COLORS['primary']])
                fig_rev.update_traces(text=daily_rev['amount_usd'].apply(lambda x: f"${x/1000:.1f}k"), textposition="top center")
                st.plotly_chart(chart_factory.styled_fig(fig_rev), use_container_width=True)
            else:
                st.info("No transaction data.")

        with col_metrics:
            st.subheader("Conversion Metrics")
            # Tính toán các chỉ số
            # 1. First Transaction Revenue: Doanh thu từ giao dịch đầu tiên của mỗi user
            first_txns = df_mon.sort_values('timestamp').groupby('user_id').first().reset_index()
            first_txn_rev = first_txns['amount_usd'].sum()
            
            # 2. Converting Users: Số user có giao dịch đầu tiên trong khoảng thời gian này
            # (Với filter cohort, đây chính là paying users)
            converting_users = paying_users 
            
            # Hiển thị dạng Card nhỏ dọc
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px;">
                <p style="margin:0; color:#6c757d; font-size:13px;">First Transaction Revenue</p>
                <h3 style="margin:5px 0; color:#007bff;">${first_txn_rev:,.0f}</h3>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px;">
                <p style="margin:0; color:#6c757d; font-size:13px;">Converting Users (First-time)</p>
                <h3 style="margin:5px 0; color:#007bff;">{converting_users:,}</h3>
            </div>
             <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6;">
                <p style="margin:0; color:#6c757d; font-size:13px;">Transactions Count</p>
                <h3 style="margin:5px 0; color:#007bff;">{len(df_mon):,}</h3>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # SECTION 3: BREAKDOWNS (Revenue by Item & Paying Users Trend)
        b1, b2 = st.columns(2)
        
        with b1:
            st.subheader("Revenue (IAP Group by Item)")
            if not df_mon.empty:
                # Group by item_id
                item_rev = df_mon.groupby('item_id')['amount_usd'].sum().sort_values(ascending=False).reset_index()
                # Bar Chart giống hình mẫu
                fig_item = px.bar(item_rev, x='item_id', y='amount_usd', 
                                  text='amount_usd', color='amount_usd', color_continuous_scale='Blues')
                fig_item.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
                fig_item.update_layout(xaxis_title=None, yaxis_title=None)
                st.plotly_chart(chart_factory.styled_fig(fig_item), use_container_width=True)
        
        with b2:
            st.subheader("Paying Users (Over Time)")
            if not df_mon.empty:
                # Count unique users per day
                daily_paying = df_mon.groupby(df_mon['timestamp'].dt.date)['user_id'].nunique().reset_index()
                daily_paying.columns = ['date', 'paying_users']
                
                # Line Chart giống hình mẫu
                fig_pu = px.line(daily_paying, x='date', y='paying_users', markers=True,
                                 color_discrete_sequence=['#007bff'])
                fig_pu.update_traces(line_shape='linear')
                st.plotly_chart(chart_factory.styled_fig(fig_pu), use_container_width=True)

    else:
        st.warning("Vui lòng chọn khoảng thời gian.")
else:
    st.error("Không tìm thấy dữ liệu.")
