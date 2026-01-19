import streamlit as st

# Định nghĩa bảng màu
COLORS = {
    'primary': '#007bff',   # Blue chuyên nghiệp
    'secondary': '#6c757d', # Xám
    'success': '#28a745',   # Xanh lá
    'warning': '#ffc107',   # Vàng
    'danger': '#dc3545',    # Đỏ
    'background': '#ffffff', # Nền trắng
    'text': '#212529'       # Chữ đen xám
}

def apply_theme():
    st.markdown(f"""
        <style>
        /* Nền của ứng dụng */
        .stApp {{
            background-color: {COLORS['background']};
            color: {COLORS['text']};
        }}
        /* Sidebar màu xám nhạt */
        [data-testid="stSidebar"] {{
            background-color: #f8f9fa;
        }}
        /* Thẻ KPI */
        .glass-card {{
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 15px;
        }}
        .glass-card h2 {{
            color: {COLORS['primary']} !important;
        }}
        .glass-card small {{
            color: {COLORS['secondary']} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
