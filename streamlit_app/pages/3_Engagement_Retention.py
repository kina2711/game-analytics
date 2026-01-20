import sys
from pathlib import Path
import streamlit as st
from datetime import date

utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path: sys.path.insert(0, utils_path)

import data_utils, config, chart_factory

st.set_page_config(page_title="Retention", layout="wide")
config.apply_theme()

raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    st.sidebar.header("Retention Filters")
    dr = st.sidebar.date_input("Install Period", [date(2025, 11, 1), date(2025, 11, 30)])
    
    if len(dr) == 2:
        data = data_utils.apply_filters(raw_data, raw_data['dim_users']['country'].unique(), ["iOS", "Android"], dr)
        
        st.title("Engagement & Retention")
        
        # 1. COHORT MATRIX
        st.subheader("User Retention Matrix (D0 - D7)")
        matrix = data_utils.get_full_cohort_matrix(data['fact_sessions'], data['dim_users'])
        chart_factory.display_cohort_style(matrix)
        
        st.divider()
        
        # 2. FUNNEL BREAKDOWN (TABLE WITH DATA LABELS)
        st.subheader("Level Completion Breakdown")
        st.markdown("Bảng phân tích tỷ lệ hoàn thành với số liệu chi tiết.")
        
        funnel_df = data_utils.get_funnel_breakdown(data['fact_gameplay_events'])
        
        if not funnel_df.empty:
            chart_factory.display_funnel_table(funnel_df)
            
            drop_max = funnel_df.loc[funnel_df['Churn Rate'].idxmax()]
            st.error(f"**Biggest Drop:** {drop_max['Step']} là điểm gãy lớn nhất ({drop_max['Churn Rate']:.1%}).")
        else:
            st.warning("Chưa có dữ liệu gameplay.")
