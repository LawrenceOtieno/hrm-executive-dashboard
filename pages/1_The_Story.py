import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

theme.inject_css()

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
gender_gap = (
    (active.groupby("Gender")["Salary"].mean()["Male"] - active.groupby("Gender")["Salary"].mean()["Female"])
    / active.groupby("Gender")["Salary"].mean()["Female"]
    * 100
)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown(
    f"<div class='section-kicker'>Workforce Analytics &middot; FY Snapshot</div>",
    unsafe_allow_html=True,
)
st.title("The Workforce Story")
st.markdown(
    "<p style='font-size:16px;'>A note from Lawrence — I pulled apart this year's headcount, "
    "pay and attrition numbers to find the signal, not just chart everything we have. "
    "Here's the short version, and the pages alongside this one dig into each thread.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ---------------------------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------------------------
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
        f"{gender_gap:.1f}%",
        "Men paid more, on average",
        tone="alert" if gender_gap > 3 else "neutral",
    )

# ---------------------------------------------------------------------------
# HEADLINE INSIGHT
# ---------------------------------------------------------------------------
theme.insight_box(
    f"Overall turnover sits at <b>{turnover_rate:.1f}%</b>, which sounds manageable on its own. "
    f"But <b>{involuntary_share:.0f}% of exits were involuntary</b> — meaning this is mostly a "
    "<b>performance and fit problem, not a retention problem</b>. That changes the fix: exit "
    "interviews and pay reviews will tell you less here than a look at hiring quality and "
    "manager decisions in the departments below.",
    tone="alert",
    label="The headline",
)

st.markdown("&nbsp;", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# HERO CHART — turnover rate by department, click to drill into who left
# ---------------------------------------------------------------------------
theme.section_header(
    "The Hero Chart",
    "Where is turnover actually concentrated?",
    "Click a bar to see who left from that department.",
)

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

fig_hero = px.bar(
    dept_summary,
    x="TurnoverRate",
    y="Department",
    orientation="h",
    text="TurnoverRate",
    color="TurnoverRate",
    color_continuous_scale=[theme.TEAL, theme.NAVY_LIGHT, theme.ORANGE, theme.ORANGE_DARK],
)
fig_hero.update_traces(texttemplate="%{text}%", textposition="outside")
fig_hero.update_coloraxes(showscale=False)
fig_hero = theme.style_fig(fig_hero, height=380, legend=False)
fig_hero.update_layout(xaxis_title="Turnover rate (%)", yaxis_title="")

clicked_dept = theme.clickable_chart(fig_hero, key="hero_dept_click", height=380)

theme.insight_box(
    f"<b>{worst_dept['Department']}</b> has the highest turnover at "
    f"<b>{worst_dept['TurnoverRate']}%</b>, more than double "
    f"<b>{best_dept['Department']}</b>'s <b>{best_dept['TurnoverRate']}%</b>. "
    "Recommended next step: start with a review of the last 12 months of performance "
    "ratings and manager decisions in the highest-turnover departments before assuming "
    "it's a pay or culture issue company-wide.",
    tone="neutral",
    label="So what",
)

# Drill-down detail table
if clicked_dept:
    st.markdown(f"#### Who left — {clicked_dept}")
    dept_leavers = left[left["Department"] == clicked_dept][
        ["EmployeeID", "FullName", "JobTitle", "Location", "TerminationType", "TenureYears", "Salary"]
    ].sort_values("TenureYears")
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
    st.markdown("**📉 Who's Leaving & Why**")
    st.caption(
        "Regional breakdown of departures, salary vs. tenure patterns, and the full roster "
        "with drill-down."
    )
with c2:
    st.markdown("**🏢 Departmental Insights**")
    st.caption(
        "Gender and age composition by department, and where involuntary exits are "
        "clustered."
    )
with c3:
    st.markdown("**📍 Regional Pay Equity**")
    st.caption(
        "Hub-by-hub pay benchmarking, plus the gender pay gap by location."
    )

theme.signature("Data reflects the current active + historical departure roster.")
