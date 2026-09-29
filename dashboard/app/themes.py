"""
Themes and styling utilities for NHL Salary Inequality Analysis Dash app.

Provides functions and constants for consistent plot and layout styling,
including color schemes, fonts, and reusable HTML components.
"""

# app/themes.py
from app.constants import *
from dash import html


def apply_plot_style(fig, title=None):
    if title:
        fig.update_layout(title=title)

    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor="#FFFFFF",
        font=dict(family="Georgia, Georgia, serif", color=PRIMARY_TEXT, size=14),
        hoverlabel=dict(bgcolor="white", font=dict(size=13)),
        margin=dict(l=20, r=20, t=50, b=20),
        height=520,
        autosize=False,
        showlegend=False,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
        zeroline=False,
        linecolor=NAVY,
        tickcolor=NAVY,
        mirror=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
        zeroline=False,
        linecolor=NAVY,
        tickcolor=NAVY,
        mirror=True,
    )
    return fig


RED_LINE = html.Hr(
    style={
        "border": "none",
        "borderTop": f"3px solid {LIGHT_RED}",
        "margin": "20px 0",
    }
)
