import plotly.express as px
import plotly.graph_objects as go
from config import COLORS

def styled_fig(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color="white", template="plotly_dark",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def plot_gauge(value, title, target=0.2):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = value,
        title = {'text': title},
        gauge = {'axis': {'range': [0, 0.5]}, 'bar': {'color': COLORS['primary']},
                 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target}}
    ))
    return styled_fig(fig)

def draw_metric(label, value, delta=None):
    delta_html = f"<p style='color:{COLORS['success']};font-size:14px;margin:0'>↑ {delta}</p>" if delta else ""
    st.markdown(f"""
    <div class="glass-card">
        <small style="color:#888">{label}</small>
        <h2 style="margin:0">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)