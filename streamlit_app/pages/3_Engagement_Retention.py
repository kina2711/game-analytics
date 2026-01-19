import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
from datetime import date

# Tự động tìm thư mục 'streamlit_app' để nạp data_utils, config, chart_factory
utils_path = str(Path(__file__).resolve().parents[1])
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

try:
    import data_utils
    import config
    import chart_factory
except ImportError as e:
    st.error(f"Không thể nạp module hỗ trợ: {e}")
    st.stop()

# 2. CẤU HÌNH TRANG
st.set_page_config(page_title="Engagement & Retention", layout="wide")
config.apply_theme() # Áp dụng Giao diện Sáng (Light Mode)

# 3. LOAD VÀ FILTER DATA
raw_data = data_utils.load_all_data()

if not raw_data['dim_users'].empty:
    # Sidebar: Bộ lọc toàn cục (Slicers)
    st.sidebar.header("Retention Filters")
    
    # Bộ lọc ngày cài đặt (Dataset tháng 11/2025)
    date_range = st.sidebar.date_input(
        "Install Date Period",
        value=(date(2025, 11, 1), date(2025, 11, 30)),
        min_value=date(2025, 1, 1),
        max_value=date(2026, 12, 31)
    )
    
    selected_countries = st.sidebar.multiselect(
        "Select Country", 
        options=raw_data['dim_users']['country'].unique(),
        default=raw_data['dim_users']['country'].unique()[:3]
    )
    
    selected_platforms = st.sidebar.multiselect(
        "Platform", 
        options=["iOS", "Android"], 
        default=["iOS", "Android"]
    )

    # Áp dụng logic lọc dữ liệu an toàn
    if len(date_range) == 2:
        data = data_utils.apply_filters(raw_data, selected_countries, selected_platforms, date_range)

        # 4. GIAO DIỆN CHÍNH
        st.title("Engagement & Retention Analytics")
        st.markdown("Phân tích mức độ gắn kết và tỷ lệ giữ chân người chơi theo thời gian.")

        # PHẦN 1: MA TRẬN COHORT RETENTION (D0 - D7)
        st.subheader("User Retention Matrix (7-Day Cohort)")
        
        # Lấy ma trận dữ liệu chuẩn mẫu (Date | Total Users | D0-D7)
        cohort_matrix = data_utils.get_full_cohort_matrix(data['fact_sessions'], data['dim_users'])
        
        if not cohort_matrix.empty:
            # Vẽ bảng dải màu xanh Gradient trên nền sáng
            chart_factory.display_cohort_style(cohort_matrix)
            
            st.info("""
            **Cách đọc bảng:** - Cột **Total Users**: Số người chơi mới cài đặt trong ngày đó.
            - Cột **Day 0**: Luôn là 100% (Ngày đầu tiên trải nghiệm).
            - Cột **Day 1**: Tỷ lệ quay lại sau 24h - Chỉ số quan trọng nhất để đánh giá sức hấp dẫn ban đầu của game.
            """)
        else:
            st.warning("Không tìm thấy dữ liệu trong khoảng thời gian này.")

        # PHẦN 2: PHỄU HOÀN THÀNH MÀN CHƠI (FUNNEL)
        st.divider()
        st.subheader("Level Completion Funnel (Diagnostic)")
        
        df_gameplay = data['fact_gameplay_events']
        if not df_gameplay.empty:
            # Tính toán số lượng user duy nhất hoàn thành mỗi Level
            funnel_df = df_gameplay[df_gameplay['event_name'] == 'level_complete']\
                        .groupby('level_id')['user_id'].nunique().reset_index()
            funnel_df = funnel_df.sort_values('level_id')
            
            fig_funnel = px.funnel(funnel_df, x='user_id', y='level_id', 
                                   title="Drop-off từ Level 1 đến 10",
                                   color_discrete_sequence=[config.COLORS['primary']])
            
            st.plotly_chart(chart_factory.styled_fig(fig_funnel), use_container_width=True)
            
            # Actionable Insight
            st.error("**Diagnostic Insight:** Tỷ lệ rụng (drop-off) tại Level 3 vẫn duy trì ở mức cao. Đề xuất team Game Design kiểm tra lại 'Out of time' events tại màn này.")
        else:
            st.info("Chưa ghi nhận sự kiện Gameplay nào.")

    else:
        st.info("Vui lòng chọn đầy đủ ngày Bắt đầu và Kết thúc trên Sidebar.")

else:
    st.error("Không thể tải dữ liệu người dùng. Vui lòng kiểm tra file dim_users.csv tại thư mục data/.")
