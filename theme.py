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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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

# Segoe UI matches Power BI's own default (and needs no setup on Windows,
# which this app is built for). Inter is the fallback for anyone opening
# it on a machine without Segoe UI installed -- it's a similar-feeling UI
# font, loaded from Google Fonts so it renders identically everywhere.
FONT_STACK = "'Segoe UI', Inter, Arial, sans-serif"

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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], [class^="st-"], [class*=" st-"],
        .stApp, .stMarkdown, .stMarkdown p, .stMarkdown li,
        .stButton button, .stDownloadButton button,
        .stTextInput input, .stSelectbox, .stMultiSelect,
        .stDataFrame, table, th, td,
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
        [data-testid="stWidgetLabel"], [data-testid="stSidebarNav"] {{
            font-family: {FONT_STACK} !important;
        }}
        .stApp {{ background-color: {OFF_WHITE}; }}
        h1, h2, h3, h4 {{ color: {NAVY} !important; font-family: {FONT_STACK} !important; }}
        p, li, span, label {{ color: {TEXT_MID}; font-family: {FONT_STACK} !important; }}

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

        /* Compact KPI tiles for the "At a Glance" grid */
        .mini-kpi {{
            background: {WHITE};
            border-radius: 8px;
            padding: 10px 14px;
            border-left: 4px solid {NAVY_LIGHT};
            box-shadow: 0 1px 3px rgba(6,40,61,0.08);
            height: 100%;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .mini-kpi:hover {{ transform: translateY(-2px); box-shadow: 0 6px 12px rgba(6,40,61,0.14); }}
        .mini-kpi.alert {{ border-left-color: {ORANGE}; }}
        .mini-kpi.good {{ border-left-color: {TEAL}; }}
        .mini-label {{
            font-size: 10.5px; font-weight: 700; letter-spacing: .03em;
            color: {TEXT_MID}; text-transform: uppercase; margin-bottom: 2px;
        }}
        .mini-value {{ font-size: 21px; font-weight: 700; color: {NAVY}; line-height: 1.1; }}

        /* Tile wrapper so the dense grid has visible card boundaries,
           like a Power BI canvas */
        .glance-tile {{
            background: {WHITE};
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(6,40,61,0.08);
            padding: 6px 6px 0 6px;
            margin-bottom: 14px;
        }}
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
        font=dict(family=FONT_STACK, color=NAVY, size=12),
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
def style_mini_fig(fig: go.Figure, title: str = None, height: int = 200):
    """
    Compact styling for small multi-tile 'at a glance' dashboards --
    minimal chrome (no gridlines, no axis titles, small fonts, tight
    margins) so 6-8 of these can sit on one screen Power-BI style.
    """
    fig.update_layout(
        height=height,
        font=dict(family=FONT_STACK, color=NAVY, size=10),
        plot_bgcolor=WHITE,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=5, r=15, t=34, b=22),
        title=dict(
            text=title or "", font=dict(size=12, color=NAVY),
            x=0.03, xanchor="left", y=0.96, yanchor="top",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True, title=None, tickfont=dict(size=9))
    fig.update_yaxes(showgrid=False, zeroline=False, automargin=True, title=None, tickfont=dict(size=9))
    return fig


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


def mini_kpi_card(label: str, value: str, tone: str = "neutral"):
    """Compact KPI tile for the dense 'At a Glance' grid."""
    tone_class = tone if tone in ("alert", "good") else ""
    st.markdown(
        f"""
        <div class="mini-kpi {tone_class}">
            <div class="mini-label">{label}</div>
            <div class="mini-value">{value}</div>
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
# NAME PRIVACY
# ---------------------------------------------------------------------------
def redact_name(full_name: str) -> str:
    """
    Redact a name to 'first letter + block characters', e.g.
    'Wainaina Joseph' -> 'W████████ J██████'. Keeps the same visual length
    as the real name (so the table doesn't look suspiciously uniform) while
    revealing nothing beyond the first initial of each word.
    """
    if not isinstance(full_name, str) or not full_name.strip():
        return full_name
    words = full_name.split(" ")
    redacted = [w[0] + "█" * (len(w) - 1) if len(w) > 1 else w for w in words]
    return " ".join(redacted)


def masked_names(df, col: str = "FullName"):
    """
    Returns a copy of df with `col` redacted, unless the analyst has
    already unlocked names for this session (see names_unlocked()) -- in
    which case the real names pass through untouched. Use this on every
    table that shows employee names.
    """
    if col not in df.columns:
        return df
    df = df.copy()
    if not names_unlocked():
        df[col] = df[col].apply(redact_name)
    return df


def analyst_name_unlock(key: str) -> bool:
    """
    DEPRECATED shim -- kept so nothing breaks if called directly.
    Use render_analyst_sidebar_unlock() + names_unlocked() instead, which
    share one passcode entry across every page for the whole session.
    """
    return names_unlocked()


def names_unlocked() -> bool:
    """Whether the analyst has unlocked names for this session."""
    return bool(st.session_state.get("analyst_names_unlocked", False))


def render_analyst_sidebar_unlock():
    """
    Renders the single, shared name-unlock control in the sidebar. Call
    this once near the top of every page. Unlocking here (with the
    ANALYST_CODE passcode) reveals redacted employee names everywhere in
    the app for the rest of the session -- on drill-down tables, the pay
    extremes audit, and the full roster alike -- so the analyst only has
    to enter the code once, not on every table separately.

    See analyst_name_unlock()'s docstring for the security caveat: this is
    a lightweight deterrent for a public-facing report, not real auth.
    """
    default_code = "letmein123"
    try:
        real_code = st.secrets.get("ANALYST_CODE", default_code)
    except Exception:
        real_code = default_code

    st.sidebar.markdown("---")
    if names_unlocked():
        st.sidebar.success("🔓 Employee names unlocked")
        if st.sidebar.button("Re-lock names", use_container_width=True):
            st.session_state["analyst_names_unlocked"] = False
            st.rerun()
    else:
        with st.sidebar.expander("🔒 Analyst access"):
            if real_code == default_code:
                st.caption(
                    "No custom access code configured — using a placeholder. "
                    "Add `ANALYST_CODE = \"your-code\"` to "
                    "`.streamlit/secrets.toml` to set your own."
                )
            entered = st.text_input("Code to reveal employee names", type="password", key="analyst_unlock_sidebar_input")
            if entered and entered == real_code:
                st.session_state["analyst_names_unlocked"] = True
                st.rerun()
            elif entered:
                st.error("Incorrect code.")


# ---------------------------------------------------------------------------
# DRILL-DOWN HELPER
# ---------------------------------------------------------------------------
def build_export_dashboard(df):
    """
    Builds ONE composite Plotly figure that mirrors the 'At a Glance' page --
    5 KPI tiles + 8 chart tiles -- so it can be exported as a single
    downloadable/shareable PNG. Kept as its own self-contained figure
    (rather than reusing the live page's individual chart objects) so it
    renders identically regardless of how the live page is laid out.
    """
    from plotly.subplots import make_subplots

    active = df[df["Status"] == "Active"]
    left = df[df["Status"] == "Left"]

    total_headcount = len(active)
    total_departures = len(left)
    turnover_rate = total_departures / (total_headcount + total_departures) * 100
    involuntary_share = (left["TerminationType"] == "Involuntary").mean() * 100
    avg_salary = active["Salary"].mean()
    gap_pct, gap_higher = gender_pay_gap(active)

    specs = [
        [{"type": "indicator"}] * 5,
        [{"type": "xy"}, {"type": "xy"}, {"type": "domain"}, {"type": "domain"}, None],
        [{"type": "xy"}, {"type": "xy"}, {"type": "xy"}, {"type": "xy"}, None],
    ]
    fig = make_subplots(
        rows=3, cols=5, specs=specs,
        row_heights=[0.22, 0.39, 0.39],
        horizontal_spacing=0.045, vertical_spacing=0.12,
        subplot_titles=[
            "", "", "", "", "",
            "Turnover % by Dept", "Turnover % by Hub", "Gender Split", "Exit Type", "",
            "Avg Salary by Hub", "Avg Salary by Dept", "Active Age Bands", "Headcount by Dept", "",
        ],
    )

    # --- Row 1: KPI indicators. Use Plotly's own number+title zones (not
    # a single hand-built HTML string with mixed font sizes) -- that's
    # what was causing the label and value text to overlap each other in
    # both the HTML and PNG exports. This is the pattern Plotly's own
    # layout engine actually spaces correctly.
    kpi_specs = [
        ("HEADCOUNT", total_headcount, {"valueformat": ",.0f"}, NAVY),
        ("TURNOVER", turnover_rate, {"valueformat": ".1f", "suffix": "%"}, ORANGE_DARK),
        ("INVOLUNTARY EXITS", involuntary_share, {"valueformat": ".0f", "suffix": "%"}, ORANGE_DARK),
        ("AVG ANNUAL SALARY", avg_salary / 1_000_000, {"valueformat": ".2f", "prefix": "KES ", "suffix": "M"}, NAVY),
        (
            f"GENDER PAY GAP ({gap_higher} higher)", gap_pct, {"valueformat": ".1f", "suffix": "%"},
            ORANGE_DARK if gap_pct > 3 else TEAL,
        ),
    ]
    for i, (label, value, number_fmt, color) in enumerate(kpi_specs, start=1):
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=value,
                number={**number_fmt, "font": {"size": 30, "color": color}},
                title={"text": label, "font": {"size": 12, "color": TEXT_MID}},
                domain={"row": 0, "column": i - 1},
            ),
            row=1, col=i,
        )

    # --- Row 2 ---
    dept_summary = df.groupby("Department")["Status"].value_counts().unstack(fill_value=0)
    dept_summary["Total"] = dept_summary.sum(axis=1)
    dept_summary["TurnoverRate"] = (dept_summary.get("Left", 0) / dept_summary["Total"] * 100).round(1)
    dept_summary = dept_summary.reset_index().sort_values("TurnoverRate")
    fig.add_trace(
        go.Bar(x=dept_summary["TurnoverRate"], y=dept_summary["Department"], orientation="h",
               marker_color=ORANGE_DARK, showlegend=False),
        row=2, col=1,
    )

    hub_summary = df.groupby("Location")["Status"].value_counts().unstack(fill_value=0)
    hub_summary["Total"] = hub_summary.sum(axis=1)
    hub_summary["TurnoverRate"] = (hub_summary.get("Left", 0) / hub_summary["Total"] * 100).round(1)
    hub_summary = hub_summary.reset_index().sort_values("TurnoverRate")
    fig.add_trace(
        go.Bar(x=hub_summary["TurnoverRate"], y=hub_summary["Location"], orientation="h",
               marker_color=[HUB_COLORS.get(l, NAVY_LIGHT) for l in hub_summary["Location"]], showlegend=False),
        row=2, col=2,
    )

    gender_split = active["Gender"].value_counts()
    fig.add_trace(
        go.Pie(labels=gender_split.index, values=gender_split.values, hole=0.55,
               marker=dict(colors=[GENDER_COLORS.get(g, NAVY_LIGHT) for g in gender_split.index]),
               textinfo="percent", showlegend=False),
        row=2, col=3,
    )

    term_split = left["TerminationType"].value_counts()
    fig.add_trace(
        go.Pie(labels=term_split.index, values=term_split.values, hole=0.55,
               marker=dict(colors=[TERMINATION_COLORS.get(t, NAVY_LIGHT) for t in term_split.index]),
               textinfo="percent", showlegend=False),
        row=2, col=4,
    )

    # --- Row 3 ---
    hub_pay = active.groupby("Location")["Salary"].mean().reset_index().sort_values("Salary")
    fig.add_trace(
        go.Bar(x=hub_pay["Salary"], y=hub_pay["Location"], orientation="h",
               marker_color=[HUB_COLORS.get(l, NAVY_LIGHT) for l in hub_pay["Location"]], showlegend=False),
        row=3, col=1,
    )

    dept_pay = active.groupby("Department")["Salary"].mean().reset_index().sort_values("Salary")
    fig.add_trace(
        go.Bar(x=dept_pay["Salary"], y=dept_pay["Department"], orientation="h",
               marker_color=NAVY_LIGHT, showlegend=False),
        row=3, col=2,
    )

    age_bins = [0, 29, 39, 49, 100]
    age_labels = ["Under 30", "30-39", "40-49", "50+"]
    age_df = active.copy()
    age_df["Age Group"] = pd.cut(age_df["Age"], bins=age_bins, labels=age_labels)
    age_counts = age_df["Age Group"].value_counts().reindex(age_labels)
    fig.add_trace(
        go.Bar(x=age_counts.index.astype(str), y=age_counts.values,
               marker_color=DEPT_COLOR_SEQUENCE[: len(age_counts)], showlegend=False),
        row=3, col=3,
    )

    dept_headcount = active["Department"].value_counts().reset_index()
    dept_headcount.columns = ["Department", "Count"]
    dept_headcount = dept_headcount.sort_values("Count")
    fig.add_trace(
        go.Bar(x=dept_headcount["Count"], y=dept_headcount["Department"], orientation="h",
               marker_color=DEPT_COLOR_SEQUENCE[: len(dept_headcount)], showlegend=False),
        row=3, col=4,
    )

    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=9))
    fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(size=9))
    fig.update_annotations(font=dict(size=13, color=NAVY))

    fig.update_layout(
        width=1500, height=860,
        paper_bgcolor=OFF_WHITE,
        plot_bgcolor=WHITE,
        font=dict(family=FONT_STACK, color=NAVY),
        margin=dict(l=30, r=30, t=95, b=40),
        title=dict(
            text="<b>HRM Executive Dashboard — At a Glance</b>",
            font=dict(size=22, color=NAVY), x=0.02, xanchor="left",
        ),
    )
    return fig


def clickable_chart(fig: go.Figure, key: str, height: int = 360, category_axis: str = "y"):
    """
    Render a plotly chart that supports click-to-drill-down, using
    Streamlit's own built-in chart-selection support (available since
    Streamlit 1.35) -- no third-party package involved.

    This deliberately does NOT use the `streamlit-plotly-events` package.
    That package bundles its own old, unmaintained copy of the JS charting
    library, which doesn't reliably understand the JSON that current
    Plotly versions produce -- on a fresh install (e.g. Streamlit
    Community Cloud, which always installs the latest Plotly), that
    mismatch silently breaks colours and text templates. Streamlit's own
    on_select support doesn't have this problem: it's maintained by
    Streamlit itself and stays in sync with whatever charting engine
    Streamlit ships, so there's no separate JS library version to drift
    out of sync with Plotly's Python output.

    category_axis: which axis carries the category to drill into. All
    four hero charts in this app are horizontal bars (orientation='h'),
    so the category (Department/Location) lives on the Y axis and the
    number lives on X -- category_axis defaults to "y" accordingly. Pass
    "x" instead if a future chart uses vertical bars with the category on
    the X axis.
    """
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        on_select="rerun",
        selection_mode="points",
        key=key,
    )
    points = (event or {}).get("selection", {}).get("points", [])
    if points:
        return points[0].get(category_axis)
    return None
