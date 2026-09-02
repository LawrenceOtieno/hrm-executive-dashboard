"""
theme.py
--------
Central design system for the HRM Executive Dashboard.

One place for colour, chart styling and small UI components (KPI cards,
insight callouts, section intros) so every page looks like it came from
the same hand instead of being three separately-generated charts stapled
together.

Maintained by Lawrence.
"""

import streamlit as st
import plotly.graph_objects as go

try:
    from streamlit_plotly_events import plotly_events
    HAS_PLOTLY_EVENTS = True
except ImportError:
    HAS_PLOTLY_EVENTS = False


# ---------------------------------------------------------------------------
# PALETTE  (from Lawrence's brand sheet)
# ---------------------------------------------------------------------------
NAVY = "#06283D"
NAVY_MID = "#0A3D5C"
NAVY_LIGHT = "#1A5276"

ORANGE = "#F5820D"
ORANGE_DARK = "#B8610A"
TEAL = "#0D9488"

BLUE = "#2196F3"
BLUE_DARK = "#1565C0"
BLUE_LIGHT = "#64B5F6"

WHITE = "#FFFFFF"
OFF_WHITE = "#F4F8FB"
TEXT_MID = "#3D6680"
TEXT_LIGHT = "#D0E8F2"
GRID = "#DCE7EF"

# Semantic aliases. Use these in chart code rather than raw hex so that
# colour keeps a consistent MEANING across every page:
#   orange  -> "this needs attention" (attrition, risk, negative deltas)
#   teal    -> "this is healthy"      (retention, positive deltas)
#   navy    -> neutral / structural
COLOR_ALERT = ORANGE
COLOR_ALERT_DARK = ORANGE_DARK
COLOR_GOOD = TEAL
COLOR_NEUTRAL = NAVY_LIGHT
COLOR_TEXT = NAVY

# Categorical palettes — deliberately avoid orange here, it's reserved
# for "pay attention" so it doesn't get diluted as just "one of four hubs".
HUB_COLORS = {
    "Nairobi": NAVY,
    "Mombasa": NAVY_LIGHT,
    "Kisumu": BLUE_DARK,
    "Nakuru": TEAL,
}

DEPT_COLOR_SEQUENCE = [NAVY, BLUE_DARK, NAVY_LIGHT, BLUE, TEAL, TEXT_MID]

GENDER_COLORS = {"Female": BLUE_DARK, "Male": NAVY_LIGHT}

TERMINATION_COLORS = {"Involuntary": ORANGE_DARK, "Voluntary": TEAL}


# ---------------------------------------------------------------------------
# PAGE / CSS SETUP
# ---------------------------------------------------------------------------
def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {OFF_WHITE}; }}
        h1, h2, h3, h4 {{ color: {NAVY} !important; }}
        p, li, span, label {{ color: {TEXT_MID}; }}

        /* KPI cards */
        .kpi-card {{
            background: {WHITE};
            border-radius: 10px;
            padding: 18px 20px;
            border-left: 5px solid {NAVY_LIGHT};
            box-shadow: 0 1px 3px rgba(6,40,61,0.08);
            height: 100%;
        }}
        .kpi-card.alert {{ border-left-color: {ORANGE}; }}
        .kpi-card.good {{ border-left-color: {TEAL}; }}
        .kpi-label {{
            font-size: 13px; font-weight: 600; letter-spacing: .02em;
            color: {TEXT_MID}; text-transform: uppercase; margin-bottom: 4px;
        }}
        .kpi-value {{ font-size: 30px; font-weight: 700; color: {NAVY}; line-height: 1.1; }}
        .kpi-sub {{ font-size: 13px; color: {TEXT_MID}; margin-top: 4px; }}

        /* Insight / callout boxes */
        .insight-box {{
            background: {WHITE};
            border-left: 5px solid {NAVY_LIGHT};
            border-radius: 8px;
            padding: 14px 18px;
            margin: 10px 0 18px 0;
            font-size: 15px;
            color: {NAVY};
            box-shadow: 0 1px 3px rgba(6,40,61,0.06);
        }}
        .insight-box.alert {{ border-left-color: {ORANGE}; background: #FFF6EC; }}
        .insight-box.good {{ border-left-color: {TEAL}; background: #EAF7F5; }}
        .insight-box b {{ color: {NAVY}; }}
        .insight-label {{
            display:inline-block; font-size: 11px; font-weight:700; letter-spacing:.06em;
            text-transform: uppercase; color: {ORANGE_DARK}; margin-bottom: 4px;
        }}
        .insight-box.good .insight-label {{ color: {TEAL}; }}
        .insight-box.neutral .insight-label {{ color: {NAVY_LIGHT}; }}

        /* Section intro */
        .section-kicker {{
            font-size: 12px; font-weight: 700; letter-spacing: .08em;
            text-transform: uppercase; color: {ORANGE_DARK}; margin-bottom: 2px;
        }}
        .section-sub {{ color: {TEXT_MID}; font-size: 15px; margin-top: -6px; }}

        /* Signature footer */
        .lawrence-sig {{
            margin-top: 40px; padding-top: 14px; border-top: 1px solid {GRID};
            font-size: 13px; color: {TEXT_MID}; font-style: italic;
        }}

        [data-testid="stSidebar"] {{ background-color: {NAVY}; }}
        [data-testid="stSidebar"] * {{ color: {TEXT_LIGHT} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# PLOTLY STYLING
# ---------------------------------------------------------------------------
def style_fig(fig: go.Figure, height: int = 340, legend: bool = True) -> go.Figure:
    """Apply the house look to any plotly figure: fonts, gridlines, backgrounds."""
    fig.update_layout(
        height=height,
        font=dict(family="Helvetica, Arial, sans-serif", color=NAVY, size=13),
        title_font=dict(size=15, color=NAVY),
        plot_bgcolor=WHITE,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# UI COMPONENTS
# ---------------------------------------------------------------------------
def kpi_card(label: str, value: str, sub: str = "", tone: str = "neutral"):
    tone_class = tone if tone in ("alert", "good") else ""
    st.markdown(
        f"""
        <div class="kpi-card {tone_class}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(text: str, tone: str = "neutral", label: str = None):
    """A short callout that states the takeaway/decision, not just the data."""
    default_labels = {"alert": "Why this matters", "good": "What's working", "neutral": "Note"}
    label = label or default_labels.get(tone, "Note")
    st.markdown(
        f"""
        <div class="insight-box {tone}">
            <div class="insight-label">{label}</div>
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(kicker: str, title: str, subtitle: str = ""):
    st.markdown(f"<div class='section-kicker'>{kicker}</div>", unsafe_allow_html=True)
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)


def signature(note: str = ""):
    st.markdown(
        f"<div class='lawrence-sig'>Analysis & commentary by Lawrence. {note}</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# DRILL-DOWN HELPER
# ---------------------------------------------------------------------------
def clickable_chart(fig: go.Figure, key: str, height: int = 360):
    """
    Render a plotly chart that supports click-to-drill-down.
    Returns the clicked point's x-category (str) or None if nothing clicked
    yet / streamlit-plotly-events isn't installed (falls back to a plain
    static chart in that case).
    """
    if not HAS_PLOTLY_EVENTS:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption(
            "Click-to-drill-down needs the `streamlit-plotly-events` package "
            "(`pip install streamlit-plotly-events`). Showing a static chart for now."
        )
        return None

    clicked = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        key=key,
        override_height=height,
    )
    if clicked:
        point = clicked[0],
        # bar/scatter clicks carry the category or value in 'x'
        return point.get("x")
    return None
