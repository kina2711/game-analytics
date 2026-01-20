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

# LOAD DATA
raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    # FILTERS
    st.sidebar.header("Monetization Filters")
    dr = st.sidebar.date_input("Period", [date(2025, 11, 1), date(2025, 11, 30)])
    countries = st.sidebar.multiselect("Country", raw_data['dim_users']['country'].unique(), raw_data['dim_users']['country'].unique()[:5])
    
    if len(dr) == 2:
        data = data_utils.apply_filters(raw_data, countries, ["iOS", "Android"], dr)
        df_mon = data['fact_monetization']
        
        st.title("Monetization Deep-dive")
        
        # SECTION 1: TOP 3 KPIs
        total_rev = df_mon['amount_usd'].sum()
        paying_users = df_mon['user_id'].nunique()
        arppu = total_rev / paying_users if paying_users > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        with c1: chart_factory.draw_metric("Total Revenue", f"${total_rev:,.0f}", "Gross Revenue")
        with c2: chart_factory.draw_metric("Paying Users", f"{paying_users:,}", "Converted Users")
        with c3: chart_factory.draw_metric("ARPPU", f"${arppu:.2f}", "Avg Rev per Paying User")
        
        st.divider()

        # SECTION 2: REVENUE TREND & CONVERSION
        col_trend, col_metrics = st.columns([2.5, 1])
        
        with col_trend:
            st.subheader("Revenue Trend")
            if not df_mon.empty:
                daily_rev = df_mon.groupby(df_mon['timestamp'].dt.date)['amount_usd'].sum().reset_index()
                fig_rev = px.line(daily_rev, x='timestamp', y='amount_usd', markers=True, 
                                  title="Daily Revenue", color_discrete_sequence=[config.COLORS['primary']])
                # Format label số tiền gọn gàng (VD: $1.2k)
                fig_rev.update_traces(text=daily_rev['amount_usd'].apply(lambda x: f"${x/1000:.1f}k"), textposition="top center")
                st.plotly_chart(chart_factory.styled_fig(fig_rev), use_container_width=True)
            else:
                st.info("No transaction data.")

        with col_metrics:
            st.subheader("Conversion Metrics")
            if not df_mon.empty:
                # 1. First Transaction Rev
                first_txns = df_mon.sort_values('timestamp').groupby('user_id').first().reset_index()
                first_txn_rev = first_txns['amount_usd'].sum()
                
                # 2. Total Transactions
                txn_count = len(df_mon)

                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px;">
                    <p style="margin:0; color:#6c757d; font-size:13px;">First Transaction Revenue</p>
                    <h3 style="margin:5px 0; color:#007bff;">${first_txn_rev:,.0f}</h3>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px;">
                    <p style="margin:0; color:#6c757d; font-size:13px;">Total Transactions</p>
                    <h3 style="margin:5px 0; color:#007bff;">{txn_count:,}</h3>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # SECTION 3: BREAKDOWNS
        b1, b2 = st.columns(2)
        
        with b1:
            st.subheader("Revenue by Pack Price")
            if not df_mon.empty:
                df_mon['pack_name'] = df_mon['amount_usd'].apply(lambda x: f"Pack ${x:.2f}")
                item_rev = df_mon.groupby('pack_name')['amount_usd'].sum().sort_values(ascending=False).reset_index()
                
                # Vẽ Bar Chart
                fig_item = px.bar(item_rev, x='pack_name', y='amount_usd', 
                                  text='amount_usd', color='amount_usd', color_continuous_scale='Blues')
                fig_item.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
                fig_item.update_layout(xaxis_title=None, yaxis_title=None)
                st.plotly_chart(chart_factory.styled_fig(fig_item), use_container_width=True)
                
                st.info("**Note:** Do dataset không có tên gói, hệ thống tự động phân loại theo mệnh giá nạp.")
            else:
                st.info("Chưa có dữ liệu giao dịch.")
        
        with b2:
            st.subheader("Paying Users Trend")
            if not df_mon.empty:
                daily_paying = df_mon.groupby(df_mon['timestamp'].dt.date)['user_id'].nunique().reset_index()
                daily_paying.columns = ['date', 'paying_users']
                
                fig_pu = px.line(daily_paying, x='date', y='paying_users', markers=True,
                                 color_discrete_sequence=['#007bff'])
                st.plotly_chart(chart_factory.styled_fig(fig_pu), use_container_width=True)

    else:
        st.warning("Vui lòng chọn khoảng thời gian.")
else:
    st.error("Không tìm thấy dữ liệu.")
