import streamlit as st

COLORS = {
    "primary": "#00d4ff",   # Neon Blue
    "secondary": "#ff007a", # Electric Pink
    "success": "#39ff14",   # Cyber Green
    "warning": "#fabb3d",   # Amber
    "danger": "#ff4b4b",    # Red
    "bg_dark": "#0e1117",
    "card_bg": "rgba(255, 255, 255, 0.05)",
    "grid": "rgba(255, 255, 255, 0.1)"
}

def apply_theme():
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLORS['bg_dark']}; color: white; }}
        [data-testid="stSidebar"] {{ background-color: #161b22; border-right: 1px solid {COLORS['grid']}; }}
        .glass-card {{
            background: {COLORS['card_bg']};
            padding: 20px;
            border-radius: 15px;
            border: 1px solid {COLORS['grid']};
            border-left: 5px solid {COLORS['primary']};
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
        }}
        h2, h3, p {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)