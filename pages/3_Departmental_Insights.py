import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="Departmental Insights", layout="wide")
theme.inject_css()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "hrm_mock_data.csv"))
    if "Status" not in df.columns:
        df["Status"] = "Active"
    return df


df = load_data()

st.markdown("<div class='section-kicker'>Chapter 2</div>", unsafe_allow_html=True)
st.title("🏢 Departmental Insights")
st.markdown(
    "Company-wide turnover hides a more useful split: **why** people are leaving each "
    "department. A department losing people to resignations needs a different response "
    "than one losing them to terminations."
)

st.sidebar.header("Filter")
all_hubs = sorted(df["Location"].unique())
selected_hubs = st.sidebar.multiselect("Regional hub:", all_hubs, default=all_hubs)
filtered_df = df[df["Location"].isin(selected_hubs)]
active_df = filtered_df[filtered_df["Status"] == "Active"]
left_df = filtered_df[filtered_df["Status"] == "Left"]

if left_df.empty:
    st.info("No departure records for this filter selection.")
    st.stop()

# ---------------------------------------------------------------------------
# HERO: involuntary exit share by department (click to see leaver detail)
# ---------------------------------------------------------------------------
theme.section_header(
    "The Hero Chart",
    "What share of exits were involuntary, by department?",
    "Click a bar to see who left and why.",
)

dept_term = left_df.groupby(["Department", "TerminationType"]).size().unstack(fill_value=0)
dept_term["Total"] = dept_term.sum(axis=1)
dept_term["InvoluntaryPct"] = (dept_term.get("Involuntary", 0) / dept_term["Total"] * 100).round(1)
dept_term = dept_term.reset_index().sort_values("InvoluntaryPct")

high_invol = dept_term.sort_values("InvoluntaryPct", ascending=False).iloc[0]
low_invol = dept_term.sort_values("InvoluntaryPct", ascending=True).iloc[0]

fig_hero = px.bar(
    dept_term, x="InvoluntaryPct", y="Department", orientation="h", text="InvoluntaryPct",
    color="InvoluntaryPct", color_continuous_scale=[theme.TEAL, theme.NAVY_LIGHT, theme.ORANGE, theme.ORANGE_DARK],
)
fig_hero.update_traces(texttemplate="%{text}%", textposition="outside", cliponaxis=False)
fig_hero.update_coloraxes(showscale=False)
fig_hero = theme.style_fig(
    fig_hero,
    title="Involuntary share of exits, by department",
    height=340,
    legend=False,
    x_values=dept_term["InvoluntaryPct"].tolist(),
)
fig_hero.update_layout(xaxis_title="Involuntary share of exits (%)", yaxis_title="")

clicked_dept = theme.clickable_chart(fig_hero, key="dept_invol_click", height=340)

theme.insight_box(
    f"<b>{high_invol['Department']}</b> exits are <b>{high_invol['InvoluntaryPct']}% involuntary</b> — "
    f"a performance-management story. <b>{low_invol['Department']}</b> sits at just "
    f"<b>{low_invol['InvoluntaryPct']}%</b>, meaning most of its departures are voluntary — "
    "worth a closer look at whether it's losing people to competitors.",
    tone="alert",
)

if clicked_dept:
    st.markdown(f"#### Departure detail — {clicked_dept}")
    detail = left_df[left_df["Department"] == clicked_dept][
        ["EmployeeID", "FullName", "JobTitle", "Location", "TerminationType", "TenureYears", "PerformanceRating"]
    ]
    st.dataframe(detail, use_container_width=True, hide_index=True)
else:
    st.caption("Tip: click a bar above to see individual departure records for that department.")

st.markdown("---")

# ---------------------------------------------------------------------------
# SUPPORTING VISUALS
# ---------------------------------------------------------------------------
theme.section_header("Supporting Detail", "Composition of the active workforce")

s1, s2 = st.columns(2)

with s1:
    if not active_df.empty:
        gender_dept = active_df.groupby(["Department", "Gender"]).size().reset_index(name="Count")
        fig_gender = px.bar(
            gender_dept, x="Department", y="Count", color="Gender", barmode="group",
            color_discrete_map=theme.GENDER_COLORS, text_auto=True,
        )
        fig_gender.update_traces(cliponaxis=False)
        fig_gender = theme.style_fig(
            fig_gender, title="Gender mix by department", height=340,
            legend_pos="top", tickangle=-20, y_values=gender_dept["Count"].tolist(), pad_frac=0.2,
        )
        fig_gender.update_layout(xaxis_title="", yaxis_title="Employees")
        st.plotly_chart(fig_gender, use_container_width=True, config={"displayModeBar": False}, key="gender_mix_chart")

with s2:
    if not active_df.empty and "Age" in active_df.columns:
        age_bins = [0, 29, 39, 49, 100]
        age_labels = ["Under 30", "30-39", "40-49", "50+"]
        age_df = active_df.copy()
        age_df["Age Group"] = pd.cut(age_df["Age"], bins=age_bins, labels=age_labels)
        age_summary = age_df.groupby(["Department", "Age Group"], observed=False).size().reset_index(name="Count")
        fig_age = px.bar(
            age_summary, x="Department", y="Count", color="Age Group", barmode="stack",
            color_discrete_sequence=theme.DEPT_COLOR_SEQUENCE, text_auto=True,
        )
        fig_age.update_traces(cliponaxis=False)
        dept_totals = age_summary.groupby("Department")["Count"].sum().tolist()
        fig_age = theme.style_fig(
            fig_age, title="Age profile by department", height=340,
            legend_pos="top", tickangle=-20, y_values=dept_totals, pad_frac=0.2,
        )
        fig_age.update_layout(xaxis_title="", yaxis_title="Employees")
        st.plotly_chart(fig_age, use_container_width=True, config={"displayModeBar": False}, key="age_profile_chart")

if not active_df.empty:
    salary_dept = active_df.groupby("Department")["Salary"].mean().reset_index().sort_values("Salary")
    fig_salary = px.bar(
        salary_dept, x="Salary", y="Department", orientation="h", color="Salary",
        color_continuous_scale=[theme.TEAL, theme.NAVY_LIGHT, theme.NAVY], text="Salary",
    )
    fig_salary.update_traces(texttemplate="KES %{text:,.0f}", textposition="outside", cliponaxis=False)
    fig_salary.update_coloraxes(showscale=False)
    fig_salary = theme.style_fig(
        fig_salary, title="Average pay by department", height=290, legend=False,
        x_values=salary_dept["Salary"].tolist(), pad_frac=0.3,
    )
    fig_salary.update_layout(xaxis_title="Average annual salary (KES)", yaxis_title="")
    st.plotly_chart(fig_salary, use_container_width=True, config={"displayModeBar": False}, key="avg_pay_dept_chart")

    with st.expander("See exact figures"):
        salary_table = active_df.groupby("Department")["Salary"].agg(["mean", "max", "min"]).reset_index()
        salary_table.columns = ["Department", "Average", "Highest", "Lowest"]
        for c in ["Average", "Highest", "Lowest"]:
            salary_table[c] = salary_table[c].apply(lambda x: f"KES {x:,.0f}")
        st.dataframe(salary_table, use_container_width=True, hide_index=True)

theme.signature()
