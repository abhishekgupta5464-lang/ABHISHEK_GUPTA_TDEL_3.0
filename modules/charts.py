"""
Chart generation module for Smart Resume Screener.
Creates interactive Plotly charts for the analytics dashboard.
"""

from typing import Any, Dict, List, Optional

import plotly.express as px
import plotly.graph_objects as go


DARK_LAYOUT = dict(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#1A1D24",
    font=dict(color="#FAFAFA", family="Inter, sans-serif"),
    margin=dict(l=40, r=40, t=60, b=40),
)

COLORS = ["#00C853", "#69F0AE", "#FFD600", "#FF9100", "#FF1744",
          "#448AFF", "#7C4DFF", "#18FFFF", "#FF4081", "#B388FF"]


def create_score_distribution_chart(distribution: Dict[str, int]) -> go.Figure:
    """Create a bar chart showing ATS score distribution across candidates."""
    fig = go.Figure(data=[
        go.Bar(
            x=list(distribution.keys()),
            y=list(distribution.values()),
            marker_color=COLORS[:len(distribution)],
            text=list(distribution.values()),
            textposition="auto",
        )
    ])
    fig.update_layout(
        title="ATS Score Distribution",
        xaxis_title="Score Range",
        yaxis_title="Number of Candidates",
        **DARK_LAYOUT,
    )
    return fig


def create_recommendation_pie_chart(distribution: Dict[str, int]) -> go.Figure:
    """Create a pie chart showing recommendation category breakdown."""
    labels = list(distribution.keys())
    values = list(distribution.values())
    colors = ["#00C853", "#69F0AE", "#FFD600", "#FF1744"]

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors[:len(labels)]),
            textinfo="label+percent",
            textfont=dict(color="#FAFAFA"),
        )
    ])
    fig.update_layout(title="Recommendation Distribution", **DARK_LAYOUT)
    return fig


def create_skill_bar_chart(skill_data: Dict[str, int], top_n: int = 10) -> go.Figure:
    """Create a horizontal bar chart of top skills across candidates."""
    items = list(skill_data.items())[:top_n]
    if not items:
        return go.Figure()

    skills, counts = zip(*items)
    fig = go.Figure(data=[
        go.Bar(
            y=[s.title() for s in skills],
            x=list(counts),
            orientation="h",
            marker_color="#448AFF",
            text=list(counts),
            textposition="auto",
        )
    ])
    fig.update_layout(
        title=f"Top {top_n} Skills",
        xaxis_title="Frequency",
        yaxis_title="Skill",
        **DARK_LAYOUT,
    )
    fig.update_yaxes(autorange="reversed")
    return fig


def create_radar_chart(scores: Dict[str, float], title: str = "Score Breakdown") -> go.Figure:
    """Create a radar chart for individual candidate score components."""
    categories = list(scores.keys())
    values = list(scores.values())

    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(0, 200, 83, 0.2)",
        line=dict(color="#00C853", width=2),
        name="Score",
    ))
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#333"),
            bgcolor="#1A1D24",
        ),
        **DARK_LAYOUT,
    )
    return fig


def create_top_candidates_chart(candidates: List[Dict[str, Any]]) -> go.Figure:
    """Create a bar chart comparing top candidates by ATS score."""
    if not candidates:
        return go.Figure()

    names = [c.get("name", "Unknown")[:20] for c in candidates]
    scores = [c.get("ats_score", 0) for c in candidates]
    colors = ["#00C853" if s >= 80 else "#FFD600" if s >= 60 else "#FF9100" for s in scores]

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=scores,
            marker_color=colors,
            text=[f"{s}%" for s in scores],
            textposition="auto",
        )
    ])
    fig.update_layout(
        title="Top Candidates by ATS Score",
        xaxis_title="Candidate",
        yaxis_title="ATS Score",
        yaxis=dict(range=[0, 100]),
        **DARK_LAYOUT,
    )
    return fig


def create_experience_histogram(distribution: Dict[str, int]) -> go.Figure:
    """Create a histogram-style chart for experience distribution."""
    fig = go.Figure(data=[
        go.Bar(
            x=list(distribution.keys()),
            y=list(distribution.values()),
            marker_color="#7C4DFF",
            text=list(distribution.values()),
            textposition="auto",
        )
    ])
    fig.update_layout(
        title="Experience Distribution",
        xaxis_title="Experience Range",
        yaxis_title="Candidates",
        **DARK_LAYOUT,
    )
    return fig


def create_match_comparison_chart(candidates: List[Dict[str, Any]]) -> go.Figure:
    """Create grouped bar chart comparing match metrics for top candidates."""
    if not candidates:
        return go.Figure()

    top = candidates[:8]
    names = [c.get("name", "?")[:15] for c in top]

    fig = go.Figure()
    metrics = [
        ("Skill Match", "skill_match", "#00C853"),
        ("Keyword Match", "keyword_match", "#448AFF"),
        ("Semantic Score", "semantic_score", "#FFD600"),
    ]

    for label, key, color in metrics:
        fig.add_trace(go.Bar(
            name=label,
            x=names,
            y=[c.get(key, 0) for c in top],
            marker_color=color,
        ))

    fig.update_layout(
        title="Match Metrics Comparison",
        barmode="group",
        xaxis_title="Candidate",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 100]),
        legend=dict(bgcolor="#1A1D24"),
        **DARK_LAYOUT,
    )
    return fig


def create_gauge_chart(score: float, title: str = "ATS Score") -> go.Figure:
    """Create a circular gauge chart for displaying ATS score."""
    color = "#00C853" if score >= 80 else "#FFD600" if score >= 60 else "#FF9100" if score >= 40 else "#FF1744"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title=dict(text=title, font=dict(color="#FAFAFA")),
        number=dict(font=dict(color="#FAFAFA", size=40)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#FAFAFA"),
            bar=dict(color=color),
            bgcolor="#1A1D24",
            bordercolor="#333",
            steps=[
                dict(range=[0, 40], color="#FF174433"),
                dict(range=[40, 60], color="#FF910033"),
                dict(range=[60, 80], color="#FFD60033"),
                dict(range=[80, 100], color="#00C85333"),
            ],
        ),
    ))
    fig.update_layout(**DARK_LAYOUT, height=300)
    return fig
