"""
theme.py
--------
Central design system for the HRM Executive Dashboard.

One place for colour, chart styling and small UI components (KPI cards,
insight callouts, section intros) so every page looks like it came from
the same hand instead of being three separately-generated charts stapled
together.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    from streamlit_plotly_events import plotly_events
    HAS_PLOTLY_EVENTS = True
except ImportError:
    HAS_PLOTLY_EVENTS = False


# ---------------------------------------------------------------------------
# PALETTE
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

COLOR_ALERT = ORANGE
COLOR_ALERT_DARK = ORANGE_DARK
COLOR_GOOD = TEAL
COLOR_NEUTRAL = NAVY_LIGHT
COLOR_TEXT = NAVY

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

        /* KPI cards -- lift slightly on hover so they read as interactive */
        .kpi-card {{
            background: {WHITE};
            border-radius: 10px;
            padding: 18px 20px;
            border-left: 5px solid {NAVY_LIGHT};
            box-shadow: 0 1px 3px rgba(6,40,61,0.08);
            height: 100%;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 18px rgba(6,40,61,0.16);
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
def style_fig(
    fig: go.Figure,
    title: str = None,
    height: int = 340,
    legend: bool = True,
    legend_pos: str = "bottom",
    x_values=None,
    y_values=None,
    tickangle: int = None,
    pad_frac: float = 0.22,
):
    """
    Apply the house look to any plotly figure AND make sure it actually fits:
      - a real, explicit chart title (never left blank -> never 'undefined')
      - automargin on both axes so long category labels are never clipped
      - optional numeric-axis padding so 'outside' text labels aren't cut off
      - optional tick rotation + legend repositioning for crowded category axes
    """
    layout_update = dict(
        height=height,
        font=dict(family="Helvetica, Arial, sans-serif", color=NAVY, size=12),
        plot_bgcolor=WHITE,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=legend,
    )
    if title:
        layout_update["title"] = dict(
            text=title, font=dict(size=15, color=NAVY),
            x=0.01, xanchor="left", y=0.98, yanchor="top",
        )
    else:
        layout_update["title"] = dict(text="")

    if legend:
        # Drop the auto-generated legend title (e.g. "Gender", "Age Group") --
        # it's redundant with the item labels and is what was overlapping the
        # chart title when the legend sat near the top of the chart.
        layout_update["legend_title_text"] = ""
        if legend_pos == "top":
            # Push the legend clearly below the chart title, with its own
            # dedicated band of margin so the two never overlap.
            layout_update["legend"] = dict(
                orientation="h", yanchor="bottom", y=1.16, xanchor="left", x=0
            )
            top_margin = 105 if title else 65
            bottom_margin = 45
        else:
            layout_update["legend"] = dict(
                orientation="h", yanchor="top", y=-0.32, xanchor="center", x=0.5
            )
            top_margin = 55 if title else 20
            bottom_margin = 90
    else:
        top_margin = 55 if title else 20
        bottom_margin = 45

    layout_update["margin"] = dict(l=10, r=25, t=top_margin, b=bottom_margin)
    fig.update_layout(**layout_update)

    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, automargin=True)

    if tickangle is not None:
        fig.update_xaxes(tickangle=tickangle)

    # Give numeric axes headroom so labels drawn "outside" the bar/marker
    # never get clipped by the edge of the plotting area.
    if x_values is not None and len(x_values):
        vmax = max(x_values)
        vmin = min(0, min(x_values))
        if vmax > 0:
            fig.update_xaxes(range=[vmin, vmax * (1 + pad_frac)])
    if y_values is not None and len(y_values):
        vmax = max(y_values)
        vmin = min(0, min(y_values))
        if vmax > 0:
            fig.update_yaxes(range=[vmin, vmax * (1 + pad_frac)])

    return fig


def build_hub_map(df, lat_col="lat", lon_col="lon", text_col="Location",
                   size_col="Total", color_col="Location", color_map=None,
                   zoom=4.6, height=280):
    """
    Build the Kenya hub map in a way that works across Plotly versions.
    Newer Plotly (>=5.24) uses px.scatter_map (MapLibre, no token needed).
    Older Plotly uses px.scatter_mapbox (also no token needed with the
    'open-street-map' / 'carto-positron' base styles). Pick whichever the
    installed version actually supports instead of hard-coding one, so this
    doesn't break again on a different machine/environment.
    """
    # No on-marker text label here on purpose: the base map tiles already
    # print each city's name (Kisumu, Nakuru, Nairobi, Mombasa...), and
    # adding our own text on top of that produced the doubled/garbled
    # labels. Hubs are instead distinguished by colour + a legend, and the
    # exact name is available on hover.
    if hasattr(px, "scatter_map"):
        fig = px.scatter_map(
            df, lat=lat_col, lon=lon_col, hover_name=text_col, size=size_col,
            color=color_col, color_discrete_map=color_map, zoom=zoom,
        )
        fig.update_layout(
            map=dict(style="carto-positron", center={"lat": -2.1, "lon": 37.3}, zoom=zoom)
        )
    else:
        fig = px.scatter_mapbox(
            df, lat=lat_col, lon=lon_col, hover_name=text_col, size=size_col,
            color=color_col, color_discrete_map=color_map, zoom=zoom,
        )
        fig.update_layout(
            mapbox=dict(style="open-street-map", center={"lat": -2.1, "lon": 37.3}, zoom=zoom)
        )

    fig.update_layout(
        height=height,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        legend_title_text="",
        margin=dict(l=0, r=0, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(text="Hub locations", font=dict(size=15, color=NAVY), x=0.01, xanchor="left"),
    )
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


def gender_pay_gap(df):
    """
    Returns (gap_pct, higher_label) where gap_pct is always a positive
    number and higher_label ('Men' / 'Women') says who actually earns
    more -- avoids a misleading negative percentage on the KPI card.
    """
    means = df.groupby("Gender")["Salary"].mean()
    male = float(means.get("Male", 0))
    female = float(means.get("Female", 0))
    if male == 0 or female == 0:
        return 0.0, "N/A"
    higher = "Men" if male >= female else "Women"
    lower = min(male, female)
    gap_pct = abs(male - female) / lower * 100
    return round(gap_pct, 1), higher


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
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key + "_static")
        st.caption(
            "Click-to-drill-down needs the `streamlit-plotly-events` package "
            "(`pip install streamlit-plotly-events`). Showing a static chart for now."
        )
        return None

    # override_height sets the *container's* pixel height. If it exactly
    # matches the figure's own height, tiny rendering overhead (borders,
    # rounding) can clip the bottom few pixels -- which is exactly what was
    # cutting off the x-axis title on these charts. Giving the container
    # some slack beyond the figure's own height fixes that without
    # changing the figure's own proportions.
    clicked = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        key=key,
        override_height=height + 45,
        override_width="100%",
    )
    if clicked:
        point = clicked[0]
        return point.get("x")
    return None
