import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import config

def draw_metric(label, value, delta=None):
    """
    Tạo card chỉ số với phong cách Glassmorphism.
    Lưu ý: CSS '.glass-card' phải được định nghĩa trong config.apply_theme().
    """
    delta_html = f"<p style='color:{config.COLORS['success']};font-size:14px;margin:0'>↑ {delta}</p>" if delta else ""
    st.markdown(f"""
    <div class="glass-card">
        <small style="color:#888; font-weight: 500;">{label}</small>
        <h2 style="margin:5px 0; color:white; font-size: 28px;">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def styled_fig(fig):
    """
    Hàm chuẩn hóa layout cho tất cả biểu đồ Plotly để khớp với giao diện Dark Mode.
    """
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    return fig

def plot_gauge(value, title, target=0.2):
    """
    Vẽ biểu đồ Gauge (Đồng hồ đo) cho các chỉ số như Stickiness (DAU/MAU).
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 18}},
        number = {'suffix': "%", 'valueformat': ".1%"},
        gauge = {
            'axis': {'range': [0, 0.5], 'tickformat': ".0%"},
            'bar': {'color': config.COLORS['primary']},
            'bgcolor': "rgba(255,255,255,0.05)",
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))
    return styled_fig(fig)

def plot_cohort_heatmap(matrix):
    """
    Vẽ ma trận Cohort Retention linh hoạt theo số lượng cột thực tế.
    """
    if matrix.empty:
        return go.Figure()

    # 1. Lấy tối đa 8 cột đầu tiên (hoặc ít hơn nếu data chưa đủ 8 ngày)
    plot_df = matrix.iloc[:, :8]
    
    # 2. Đếm số lượng cột thực tế đang có
    actual_col_count = plot_df.shape[1]
    
    # 3. Tạo nhãn tương ứng với số cột thực tế
    x_labels = [f"Day {i}" for i in range(actual_col_count)]
    
    # 4. Vẽ biểu đồ
    fig = px.imshow(
        plot_df,
        text_auto=".1%", # Hiển thị tỷ lệ %
        color_continuous_scale=[[0, "#161b22"], [1, config.COLORS['primary']]],
        labels=dict(x="Day Since Install", y="Cohort Date", color="Retention %"),
        x=x_labels # Sử dụng danh sách nhãn linh hoạt
    )
    
    fig.update_layout(
        title="User Retention Cohort Heatmap (D0 - Dn)",
        coloraxis_showscale=False,
        xaxis_nticks=actual_col_count # Đảm bảo vạch chia khớp với số cột
    )
    
    return styled_fig(fig)
