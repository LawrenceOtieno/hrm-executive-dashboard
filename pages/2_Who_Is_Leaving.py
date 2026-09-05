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

st.markdown("<div class='section-kicker'>Chapter 1</div>", unsafe_allow_html=True)
st.title("📉 Who's Leaving, and Why")
st.markdown(
    "Turnover isn't spread evenly across hubs. This page isolates *where* it's "
    "concentrated and whether pay or tenure explain it — before pointing at any "
    "one location."
)

# SIDEBAR FILTER
st.sidebar.header("Filter")
selected_location = st.sidebar.multiselect(
    "Regional hub:", options=sorted(df["Location"].unique()), default=sorted(df["Location"].unique())
)
filtered_df = df[df["Location"].isin(selected_location)]
active = filtered_df[filtered_df["Status"] == "Active"]
left = filtered_df[filtered_df["Status"] == "Left"]

total_headcount = len(active)
attrition_count = len(left)
pool = total_headcount + attrition_count
turnover_rate = (attrition_count / pool * 100) if pool else 0
avg_salary = active["Salary"].mean() if total_headcount else 0
avg_tenure_leavers = left["TenureYears"].mean() if attrition_count else 0

st.markdown("---")
k1, k2, k3, k4 = st.columns(4)
with k1:
    theme.kpi_card("Active Headcount", f"{total_headcount:,}")
with k2:
    theme.kpi_card("Turnover Rate", f"{turnover_rate:.1f}%", f"{attrition_count} left", tone="alert")
with k3:
    theme.kpi_card("Avg Salary (Active)", f"KES {avg_salary:,.0f}", "Annual")
with k4:
    theme.kpi_card("Avg Tenure at Exit", f"{avg_tenure_leavers:.1f} yrs")

st.markdown("---")

if total_headcount == 0:
    st.info("Select at least one hub from the sidebar to see the story.")
    st.stop()

# ---------------------------------------------------------------------------
# HERO: turnover rate by hub, click to drill into leaver roster
# ---------------------------------------------------------------------------
theme.section_header(
    "The Hero Chart", "Turnover rate by hub", "Click a bar to see who left from that hub."
)

hub_summary = (
    filtered_df.groupby("Location")["Status"].value_counts().unstack(fill_value=0)
)
hub_summary["Total"] = hub_summary.sum(axis=1)
hub_summary["TurnoverRate"] = (hub_summary.get("Left", 0) / hub_summary["Total"] * 100).round(1)
hub_summary = hub_summary.reset_index().sort_values("TurnoverRate")

worst_hub = hub_summary.sort_values("TurnoverRate", ascending=False).iloc[0]
best_hub = hub_summary.sort_values("TurnoverRate", ascending=True).iloc[0]

fig_hero = px.bar(
    hub_summary,
    x="TurnoverRate",
    y="Location",
    orientation="h",
    text="TurnoverRate",
    color="Location",
    color_discrete_map=theme.HUB_COLORS,
)
fig_hero.update_traces(texttemplate="%{text}%", textposition="outside", cliponaxis=False)
fig_hero = theme.style_fig(
    fig_hero,
    title="Turnover rate by hub",
    height=320,
    legend=False,
    x_values=hub_summary["TurnoverRate"].tolist(),
)
fig_hero.update_layout(xaxis_title="Turnover rate (%)", yaxis_title="")

clicked_hub = theme.clickable_chart(fig_hero, key="hub_turnover_click", height=320)

theme.insight_box(
    f"<b>{worst_hub['Location']}</b> loses staff faster than any other city, at "
    f"<b>{worst_hub['TurnoverRate']}%</b>, compared with <b>{best_hub['Location']}</b>'s "
    f"<b>{best_hub['TurnoverRate']}%</b>. Before assuming this is about pay, look at the salary "
    "chart below — the pay gap between cities is much smaller than the gap in how many people "
    "leave. That usually means the real cause is how the office is run or how heavy the workload "
    "is, not how much people are paid.",
    tone="alert",
)

if clicked_hub:
    st.markdown(f"#### Who left — {clicked_hub}")
    hub_leavers = left[left["Location"] == clicked_hub][
        ["EmployeeID", "FullName", "Department", "JobTitle", "TerminationType", "TenureYears", "Salary"]
    ].sort_values("TenureYears")
    hub_leavers = theme.masked_names(hub_leavers)
    if not theme.names_unlocked():
        st.caption("🔒 Names redacted — unlock in the sidebar (Analyst access) to reveal.")
    st.dataframe(
        hub_leavers.style.format({"Salary": "KES {:,.0f}", "TenureYears": "{:.1f} yrs"}),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.caption("Tip: click a bar above to see the individual departure records.")

st.markdown("---")

# ---------------------------------------------------------------------------
# SUPPORTING VISUALS (secondary — smaller, side by side)
# ---------------------------------------------------------------------------
theme.section_header("Supporting Detail", "Does pay or tenure explain the gap?")

s1, s2 = st.columns(2)

with s1:
    hub_pay = active.groupby("Location")["Salary"].mean().reset_index().sort_values("Salary")
    fig_pay = px.bar(
        hub_pay, x="Salary", y="Location", orientation="h", color="Location",
        color_discrete_map=theme.HUB_COLORS, text="Salary",
    )
    fig_pay.update_traces(texttemplate="KES %{text:,.0f}", textposition="outside", cliponaxis=False)
    fig_pay = theme.style_fig(
        fig_pay, title="Average salary by hub", height=270, legend=False,
        x_values=hub_pay["Salary"].tolist(), pad_frac=0.35,
    )
    fig_pay.update_layout(xaxis_title="KES", yaxis_title="")
    st.plotly_chart(fig_pay, use_container_width=True, config={"displayModeBar": False}, key="salary_by_hub_chart")

with s2:
    hub_rel = active.groupby("Location").agg(
        Average_Tenure_Years=("TenureYears", "mean"),
        Average_Salary=("Salary", "mean"),
        Employee_Count=("EmployeeID", "count"),
    ).reset_index()
    fig_rel = px.scatter(
        hub_rel, x="Average_Tenure_Years", y="Average_Salary", color="Location",
        color_discrete_map=theme.HUB_COLORS, text="Location", size="Employee_Count", size_max=28,
    )
    fig_rel.update_traces(textposition="top center")
    fig_rel = theme.style_fig(
        fig_rel, title="Tenure vs. salary, by hub", height=270, legend=False,
        y_values=hub_rel["Average_Salary"].tolist(), pad_frac=0.15,
    )
    fig_rel.update_layout(xaxis_title="Avg tenure (yrs)", yaxis_title="Avg salary (KES)")
    st.plotly_chart(fig_rel, use_container_width=True, config={"displayModeBar": False}, key="tenure_salary_chart")

s3, s4 = st.columns(2)
with s3:
    fig_donut = px.pie(
        hub_summary, values="Total", names="Location", hole=0.5,
        color="Location", color_discrete_map=theme.HUB_COLORS,
    )
    fig_donut.update_traces(textinfo="percent", textfont=dict(size=12, color=theme.WHITE))
    fig_donut = theme.style_fig(fig_donut, title="Headcount distribution", height=270)
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False}, key="headcount_donut_chart")

with s4:
    geo_coords = {
        "Nairobi": {"lat": -1.2921, "lon": 36.8219},
        "Mombasa": {"lat": -4.0435, "lon": 39.6682},
        "Kisumu": {"lat": -0.1022, "lon": 34.7617},
        "Nakuru": {"lat": -0.3031, "lon": 36.0800},
    }
    hub_summary["lat"] = hub_summary["Location"].map(lambda x: geo_coords.get(x, {}).get("lat", 0.0))
    hub_summary["lon"] = hub_summary["Location"].map(lambda x: geo_coords.get(x, {}).get("lon", 0.0))
    fig_map = theme.build_hub_map(
        hub_summary, color_map=theme.HUB_COLORS, zoom=4.6, height=270,
    )
    st.plotly_chart(fig_map, use_container_width=True, key="hub_locations_map")

st.markdown("---")

# ---------------------------------------------------------------------------
# FULL ROSTER
# ---------------------------------------------------------------------------
theme.section_header("Reference", "Full employee roster")
selected_status = st.segmented_control(
    "Filter by status:", options=["All Staff", "Active Only", "Left Only"], default="All Staff"
)
display_df = filtered_df.copy()
if selected_status == "Active Only":
    display_df = display_df[display_df["Status"] == "Active"]
elif selected_status == "Left Only":
    display_df = display_df[display_df["Status"] == "Left"]

display_cols = ["EmployeeID", "FullName", "Status", "Gender", "Age", "Department", "JobTitle", "Location", "TerminationType", "Salary"]
display_df = display_df[[c for c in display_cols if c in display_df.columns]]

# Names are the only field masked by default -- everything else here is
# fine for anyone to see. Unlock once in the sidebar (Analyst access) and
# real names show on every table across the whole app for this session.
display_df = theme.masked_names(display_df)
if theme.names_unlocked():
    st.caption("🔓 Names unlocked for this session.")
else:
    st.caption("🔒 Employee names are redacted. Unlock in the sidebar (Analyst access) to reveal them.")

st.dataframe(
    display_df.style.format({"Salary": "KES {:,.0f}"}),
    use_container_width=True,
    hide_index=True,
)

theme.signature()
