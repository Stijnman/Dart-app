
"""
Advanced Heat Maps for Dart Game Pro v2.4
Implements / enhances Feature #15: Advanced Heat Maps (3D visualization, consistency clusters, drift trends)

Replaces or extends basic VirtualDartboard heatmap.
Recommends: pip install plotly (for interactive 3D + nice viz in Streamlit)
Fallback to matplotlib 3D if plotly not available.

Key new capabilities:
- 3D scatter / surface of throw locations over time
- Consistency clusters (simple KMeans or density-based grouping)
- Drift trends (throw # vs deviation from mean, color coded by session)
- Integration with existing throw history from player or game_state
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D  # for 3D

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("Plotly not installed. Using matplotlib fallback. For best experience: pip install plotly")

# Simple dartboard coordinate mapping (example - expand with your existing VirtualDartboard logic)
# Assume throws are list of dicts: [{'x': float, 'y': float, 'score': int, 'timestamp': str or int, 'visit': int}, ...]
# x,y normalized -1 to 1 or 0-20 for board units. You can map from your existing segment hit logic.

def generate_advanced_heatmap(
    throws: List[Dict[str, Any]],
    player_name: str = "Player",
    use_plotly: bool = True,
    show_clusters: bool = True,
    show_drift: bool = True
) -> Tuple[Any, str]:
    """
    Generate advanced heatmap figure + summary text.
    Returns (figure, analysis_summary_markdown)
    """
    if not throws:
        return None, "No throw data available for heatmap."

    # Extract data
    xs = np.array([t.get('x', np.random.uniform(-1,1)) for t in throws])  # replace with real coords from your engine
    ys = np.array([t.get('y', np.random.uniform(-1,1)) for t in throws])
    scores = np.array([t.get('score', 0) for t in throws])
    visit_nums = np.array([t.get('visit', i//3) for i, t in enumerate(throws)])  # group by visits/legs
    timestamps = np.arange(len(throws))  # or parse real time for drift

    summary_lines = [f"### 🎯 Advanced Heatmap Analysis for {player_name}"]
    summary_lines.append(f"- Total throws analyzed: {len(throws)}")
    summary_lines.append(f"- Average score: {np.mean(scores):.1f}")
    summary_lines.append(f"- Consistency (std dev of scores): {np.std(scores):.2f}")

    fig = None
    title = f"Advanced Throw Heatmap - {player_name}"

    if HAS_PLOTLY and use_plotly:
        # Interactive Plotly version (recommended for Streamlit)
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{ "type": "scene"}, {"type": "xy"}],
                   [{"type": "xy"}, {"type": "xy"}]],
            subplot_titles=("3D Throw Trajectory + Clusters", "2D Density Heatmap", 
                            "Drift Over Time (Score)", "Consistency Clusters (2D)"),
            vertical_spacing=0.12
        )

        # 1. 3D scatter with time as z (drift in 3D)
        fig.add_trace(
            go.Scatter3d(
                x=xs, y=ys, z=timestamps,
                mode='markers',
                marker=dict(
                    size=5,
                    color=scores,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Score")
                ),
                text=[f"Visit {v}<br>Score {s}" for v,s in zip(visit_nums, scores)],
                name="Throws 3D"
            ),
            row=1, col=1
        )

        # 2. 2D density heatmap (classic + advanced)
        fig.add_trace(
            go.Histogram2dContour(
                x=xs, y=ys,
                colorscale='Hot',
                showscale=False,
                name="Density"
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=xs, y=ys, mode='markers', marker=dict(size=4, color='white', opacity=0.6), name="Throws"),
            row=1, col=2
        )

        # 3. Drift trend (score over throw number, color by visit)
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=scores,
                mode='lines+markers',
                marker=dict(color=visit_nums, colorscale='Portland', size=6),
                line=dict(width=1),
                name="Score Drift"
            ),
            row=2, col=1
        )
        # Add trend line
        z = np.polyfit(timestamps, scores, 1)
        p = np.poly1d(z)
        fig.add_trace(
            go.Scatter(x=timestamps, y=p(timestamps), mode='lines', line=dict(dash='dash', color='red'), name="Trend"),
            row=2, col=1
        )

        # 4. Clusters (simple binning or fake KMeans for demo)
        if show_clusters and len(throws) > 5:
            # Simple density clusters via binning for demo (replace with sklearn KMeans if desired)
            from scipy import stats  # or implement simple
            # For demo: color points by score clusters
            cluster_colors = np.digitize(scores, bins=[20, 40, 60, 80, 100, 120, 140, 160])
            fig.add_trace(
                go.Scatter(
                    x=xs, y=ys,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=cluster_colors,
                        colorscale='Rainbow',
                        showscale=True,
                        colorbar=dict(title="Score Cluster")
                    ),
                    text=[f"Cluster {c}" for c in cluster_colors],
                    name="Consistency Clusters"
                ),
                row=2, col=2
            )

        fig.update_layout(
            height=900,
            title_text=title,
            showlegend=True,
            scene=dict(
                xaxis_title="X (board)",
                yaxis_title="Y (board)",
                zaxis_title="Throw # (time)"
            )
        )

        summary_lines.append("- Interactive 3D + density + drift + clusters generated with Plotly.")
        summary_lines.append("- **Tip**: Install `plotly` for best interactive experience in Streamlit (`st.plotly_chart(fig)`).")

    else:
        # Matplotlib fallback (3D + 2D)
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle(title, fontsize=16)

        # 3D
        ax1 = fig.add_subplot(221, projection='3d')
        scatter = ax1.scatter(xs, ys, timestamps, c=scores, cmap=cm.viridis, s=40, alpha=0.8)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Throw #')
        fig.colorbar(scatter, ax=ax1, label='Score')
        ax1.set_title("3D Trajectory (time as depth)")

        # 2D density
        ax2 = fig.add_subplot(222)
        hb = ax2.hexbin(xs, ys, gridsize=25, cmap='hot', mincnt=1)
        ax2.scatter(xs, ys, c='white', s=10, alpha=0.5)
        ax2.set_title("2D Density Heatmap")
        fig.colorbar(hb, ax=ax2, label='Count')

        # Drift
        ax3 = fig.add_subplot(223)
        ax3.scatter(timestamps, scores, c=visit_nums, cmap='coolwarm', s=30)
        ax3.plot(timestamps, np.poly1d(np.polyfit(timestamps, scores, 1))(timestamps), 'r--', label='Trend')
        ax3.set_xlabel('Throw Number')
        ax3.set_ylabel('Score')
        ax3.set_title("Drift Trend Over Session")
        ax3.legend()

        # Clusters (color by binned score)
        ax4 = fig.add_subplot(224)
        cluster_id = np.digitize(scores, bins=[0, 40, 80, 120, 160])
        ax4.scatter(xs, ys, c=cluster_id, cmap='tab10', s=50, alpha=0.7)
        ax4.set_title("Score-based Consistency Clusters")
        ax4.set_xlabel('X')
        ax4.set_ylabel('Y')

        plt.tight_layout()

        summary_lines.append("- Matplotlib 3D + multi-panel fallback used (install plotly for interactive version).")

    # Add cluster / drift insights
    if show_drift:
        early_avg = np.mean(scores[:max(3, len(scores)//3)]) if len(scores) > 3 else np.mean(scores)
        late_avg = np.mean(scores[-max(3, len(scores)//3):]) if len(scores) > 3 else np.mean(scores)
        drift = late_avg - early_avg
        trend = "improving" if drift > 5 else ("declining" if drift < -5 else "stable")
        summary_lines.append(f"- **Drift Trend**: {trend} ({drift:+.1f} avg score change from early to late session)")

    if show_clusters:
        high_consistency = np.sum((scores > 80) & (np.abs(scores - np.mean(scores)) < 15)) / len(scores) * 100
        summary_lines.append(f"- **Consistency Clusters**: ~{high_consistency:.0f}% of throws in high-consistency band (near personal avg).")

    analysis_md = "\n".join(summary_lines)
    return fig, analysis_md


# Example usage in Streamlit analytics tab:
"""
import streamlit as st
from advanced_heatmap import generate_advanced_heatmap

# Assume you have player throws from DB or game_state['throw_history']
throws_data = st.session_state.get('current_player_throws', [])

if throws_data:
    fig, analysis = generate_advanced_heatmap(throws_data, player_name="Emerald Parker", use_plotly=True)
    if fig:
        if HAS_PLOTLY:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.pyplot(fig)
    st.markdown(analysis)
else:
    st.info("Play some games to generate advanced heatmaps!")
"""

# Future improvements:
# - Real x/y coordinates from your dartboard hit detection or VirtualDartboard
# - Integrate with existing PatternDetector for more insights
# - Add session comparison (this game vs career avg)
# - Export as PNG/PDF or interactive HTML
