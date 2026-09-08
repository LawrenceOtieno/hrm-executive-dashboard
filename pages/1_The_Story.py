import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

theme.inject_css()
theme.render_analyst_sidebar_unlock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "hrm_mock_data.csv"))
    if "Status" not in df.columns:
        df["Status"] = "Active"
    return df


df = load_data()
active = df[df["Status"] == "Active"]
left = df[df["Status"] == "Left"]

total_headcount = len(active)
total_departures = len(left)
turnover_rate = total_departures / (total_headcount + total_departures) * 100
involuntary_share = (left["TerminationType"] == "Involuntary").mean() * 100
gap_pct, gap_higher = theme.gender_pay_gap(active)

dept_summary = (
    df.groupby("Department")["Status"]
    .value_counts()
    .unstack(fill_value=0)
)
dept_summary["Total"] = dept_summary.sum(axis=1)
dept_summary["TurnoverRate"] = (dept_summary.get("Left", 0) / dept_summary["Total"] * 100).round(1)
dept_summary = dept_summary.reset_index().sort_values("TurnoverRate", ascending=True)

worst_dept = dept_summary.sort_values("TurnoverRate", ascending=False).iloc[0]
best_dept = dept_summary.sort_values("TurnoverRate", ascending=True).iloc[0]

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown(
    "<div class='section-kicker'>Workforce Analytics &middot; FY Snapshot</div>",
    unsafe_allow_html=True,
)
st.title("The Workforce Story")

facts = theme.core_story_facts(df)
theme.story_banner(facts)

# ---------------------------------------------------------------------------
# THE NARRATIVE — company context, then the shift, told as a story rather
# than a spec sheet. Every number here is pulled live from core_story_facts,
# not written in by hand.
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <p style='font-size:16px; line-height:1.7;'>
    For the better part of a decade, <b>SimbaNet Solutions</b> has been quietly rewiring how
    Kenya gets online — trenching fibre down streets in Nairobi, Mombasa, Kisumu, and Nakuru,
    lighting up homes and businesses that never had a reliable connection before. It's slow,
    technical work, done by engineers who know their section of cable the way a doctor knows a
    patient's chart, and sales teams who spend months earning a client's trust before a single
    contract gets signed.
    </p>
    <p style='font-size:16px; line-height:1.7;'>
    But somewhere behind the growth numbers, a quieter pattern took hold. People who understood
    the network — who'd spent years learning it street by street — started walking out the door.
    By the end of the year, SimbaNet was losing roughly
    <b>{facts['turnover_rate']:.0f} out of every 100 people</b> on its payroll. In a business built
    on institutional memory, that's not a line on a spreadsheet. It's a splice point nobody else
    knows how to find, a client relationship starting over from zero, and a replacement who won't
    be fully useful for months.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="insight-box alert" style="font-size:17px; padding:20px 24px;">
        <div class="insight-label">The key finding</div>
        Ask anyone at SimbaNet why people are leaving, and the first guess is almost always pay.
        The data doesn't agree. <b>{facts['worst_dept']}</b> loses people faster than any team in
        the company, at <b>{facts['worst_dept_rate']:.0f}%</b> — and look closer, and an
        uncomfortable pattern shows up: <b>{facts['involuntary_share']:.0f} out of every 100
        departures</b>, company-wide, weren't resignations. They were the company's decision.
        That reframes the whole problem. This isn't staff walking away from SimbaNet.
        It's SimbaNet walking away from staff — and that's a hiring and management story,
        not a retention one.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("&nbsp;", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# THE EVIDENCE — KPI ROW
# ---------------------------------------------------------------------------
st.markdown("#### The numbers behind that finding")
k1, k2, k3, k4 = st.columns(4)
with k1:
    theme.kpi_card("Active Headcount", f"{total_headcount:,}", "Across 4 hubs")
with k2:
    theme.kpi_card(
        "Turnover Rate",
        f"{turnover_rate:.1f}%",
        f"{total_departures} departures this year",
        tone="alert",
    )
with k3:
    theme.kpi_card(
        "Involuntary Exits",
        f"{involuntary_share:.0f}%",
        "Of all departures — not resignations",
        tone="alert",
    )
with k4:
    theme.kpi_card(
        "Gender Pay Gap",
        f"{gap_pct:.1f}%",
        f"{gap_higher} paid more, on average",
        tone="alert" if gap_pct > 3 else "neutral",
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# HERO CHART — turnover rate by department, click to drill into who left
# Decluttered: every bar is grey except the one that matters, which is
# highlighted and annotated directly, so the chart makes the point on its
# own instead of needing to be read carefully.
# ---------------------------------------------------------------------------
theme.section_header(
    "The Hero Chart",
    "Where is turnover actually concentrated?",
)
st.markdown(
    "<p style='font-size:14.5px; margin-top:-8px;'>Here's what it looks like when we open up "
    "the company team by team. Click a bar to see exactly who left from that team.</p>",
    unsafe_allow_html=True,
)

bar_colors = [
    theme.ORANGE_DARK if d == worst_dept["Department"] else theme.GRAY_MUTED
    for d in dept_summary["Department"]
]

fig_hero = px.bar(
    dept_summary,
    x="TurnoverRate",
    y="Department",
    orientation="h",
    text="TurnoverRate",
)
fig_hero.update_traces(
    marker_color=bar_colors,
    texttemplate="%{text}%", textposition="outside", cliponaxis=False,
)
fig_hero = theme.style_fig(
    fig_hero,
    title="Turnover rate by department",
    height=380,
    legend=False,
    x_values=dept_summary["TurnoverRate"].tolist(),
)
fig_hero.update_layout(xaxis_title="Turnover rate (%)", yaxis_title="")
fig_hero.add_annotation(
    x=worst_dept["TurnoverRate"],
    y=worst_dept["Department"],
    text="Highest turnover — start here",
    showarrow=True, arrowhead=2, arrowcolor=theme.ORANGE_DARK,
    ax=55, ay=-32,
    font=dict(color=theme.ORANGE_DARK, size=12, family=theme.FONT_STACK),
)

clicked_dept = theme.clickable_chart(fig_hero, key="hero_dept_click", height=380)

theme.insight_box(
    f"<b>{worst_dept['Department']}</b> loses staff faster than any other department, at "
    f"<b>{worst_dept['TurnoverRate']}%</b> — more than double "
    f"<b>{best_dept['Department']}</b>'s <b>{best_dept['TurnoverRate']}%</b>. "
    "A good next step: look closely at how staff have been rated and managed in this department "
    "over the last year, before assuming it's about pay or workplace culture everywhere.",
    tone="neutral",
    label="So what",
)

# Drill-down detail table
if clicked_dept:
    st.markdown(f"#### Who left — {clicked_dept}")
    dept_leavers = left[left["Department"] == clicked_dept][
        ["EmployeeID", "FullName", "JobTitle", "Location", "TerminationType", "TenureYears", "Salary"]
    ].sort_values("TenureYears")
    dept_leavers = theme.masked_names(dept_leavers)
    if not theme.names_unlocked():
        st.caption("Names redacted — unlock in the sidebar (Analyst access) to reveal.")
    st.dataframe(
        dept_leavers.style.format({"Salary": "KES {:,.0f}", "TenureYears": "{:.1f} yrs"}),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.caption("Tip: click any bar above to see the individual departure records behind it.")

st.markdown("---")

# ---------------------------------------------------------------------------
# WHAT'S ON THE OTHER PAGES
# ---------------------------------------------------------------------------
theme.section_header("Keep Reading", "Where each page picks up the thread")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Who's Leaving & Why**")
    st.caption(
        "Regional breakdown of departures, salary vs. tenure patterns, and the full roster "
        "with drill-down."
    )
with c2:
    st.markdown("**Departmental Insights**")
    st.caption(
        "Gender and age composition by department, and where involuntary exits are "
        "clustered."
    )
with c3:
    st.markdown("**Regional Pay Equity**")
    st.caption(
        "Hub-by-hub pay benchmarking, plus the gender pay gap by location."
    )

theme.signature("Data reflects the current active + historical departure roster.")
