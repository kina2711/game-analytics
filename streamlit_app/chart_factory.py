import plotly.express as px
import plotly.graph_objects as go
from config import COLORS

def plot_cohort_heatmap(matrix):
    """Vẽ Heatmap Retention với màu sắc Cyberpunk."""
    # Chỉ lấy D0 đến D7 để hiển thị rõ nét trên Dashboard
    plot_df = matrix.iloc[:, :8]

    fig = px.imshow(
        plot_df,
        text_auto=".1%",  # Hiển thị % trực tiếp trên ô
        color_continuous_scale=[[0, "#161b22"], [1, COLORS['primary']]],
        labels=dict(x="Day Since Install", y="Cohort Date", color="Retention %"),
        x=[f"Day {i}" for i in range(8)]
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        title="D1 - D7 User Retention Cohort"
    )
    return fig
