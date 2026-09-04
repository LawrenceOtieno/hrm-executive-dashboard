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
active_df = df[df["Status"] == "Active"]

st.markdown("<div class='section-kicker'>Chapter 3</div>", unsafe_allow_html=True)
st.title("📍 Regional Pay Equity")
st.markdown(
    "If turnover isn't purely pay-driven (see Chapter 1), is pay itself fair — across "
    "hubs, and across gender within each hub? This page checks both."
)

hub_pay = active_df.groupby("Location")["Salary"].agg(["mean", "max", "min"]).reset_index()
hub_pay.columns = ["Location", "Average", "Highest", "Lowest"]
hub_pay = hub_pay.sort_values("Average", ascending=False)

overall_gap_pct, overall_gap_higher = theme.gender_pay_gap(active_df)

st.markdown("---")
k1, k2, k3 = st.columns(3)
with k1:
    theme.kpi_card("Highest-Paying Hub", hub_pay.iloc[0]["Location"], f"KES {hub_pay.iloc[0]['Average']:,.0f} avg")
with k2:
    theme.kpi_card("Lowest-Paying Hub", hub_pay.iloc[-1]["Location"], f"KES {hub_pay.iloc[-1]['Average']:,.0f} avg")
with k3:
    theme.kpi_card(
        "Company-wide Gender Pay Gap",
        f"{overall_gap_pct:.1f}%",
        f"{overall_gap_higher} earn more, on average",
        tone="alert" if overall_gap_pct > 3 else "good",
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# HERO: avg salary by hub, click to drill into top/bottom earners
# ---------------------------------------------------------------------------
theme.section_header(
    "The Hero Chart", "Average annual pay by hub", "Click a bar to audit that hub's pay extremes."
)

fig_hero = px.bar(
    hub_pay, x="Average", y="Location", orientation="h", color="Location",
    color_discrete_map=theme.HUB_COLORS, text="Average",
)
fig_hero.update_traces(
    texttemplate="KES %{text:,.0f}", textposition="inside", insidetextanchor="end",
    textfont_color=theme.WHITE, cliponaxis=False,
)
fig_hero = theme.style_fig(
    fig_hero, title="Average annual pay by hub", height=300, legend=False,
    x_values=hub_pay["Average"].tolist(), pad_frac=0.08,
)
fig_hero.update_layout(xaxis_title="Average annual salary (KES)", yaxis_title="")

clicked_hub = theme.clickable_chart(fig_hero, key="hub_pay_click", height=300)

spread = hub_pay["Average"].max() - hub_pay["Average"].min()
theme.insight_box(
    f"The gap between the highest- and lowest-paying hub is about "
    f"<b>KES {spread:,.0f}</b> a year — roughly "
    f"{spread / hub_pay['Average'].min() * 100:.1f}% of the lowest hub's average. "
    "That's a modest spread, which supports the earlier finding that pay alone doesn't "
    "explain why turnover varies so much by location.",
    tone="neutral",
)

st.markdown("#### Pay extremes audit")
audit_hub = clicked_hub if clicked_hub else st.selectbox(
    "Or pick a hub manually:", options=sorted(active_df["Location"].unique())
)
if audit_hub:
    hub_df = active_df[active_df["Location"] == audit_hub]
    max_sal, min_sal = hub_df["Salary"].max(), hub_df["Salary"].min()
    extremes = hub_df[(hub_df["Salary"] == max_sal) | (hub_df["Salary"] == min_sal)].copy()
    extremes["Pay Tier"] = extremes["Salary"].apply(lambda x: "📈 Top Earner" if x == max_sal else "📉 Bottom Earner")
    cols = ["Pay Tier", "EmployeeID", "FullName", "Gender", "Department", "JobTitle", "Salary"]
    extremes = theme.masked_names(extremes)
    if not theme.names_unlocked():
        st.caption("🔒 Names redacted — unlock in the sidebar (Analyst access) to reveal.")
    st.dataframe(
        extremes[[c for c in cols if c in extremes.columns]].sort_values("Salary", ascending=False)
        .style.format({"Salary": "KES {:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# SUPPORTING: gender pay gap by hub + salary extremes by hub
# ---------------------------------------------------------------------------
theme.section_header("Supporting Detail", "Is the gender pay gap consistent across hubs?")

s1, s2 = st.columns(2)
with s1:
    gender_hub = active_df.groupby(["Location", "Gender"])["Salary"].mean().reset_index()
    fig_gender_hub = px.bar(
        gender_hub, x="Location", y="Salary", color="Gender", barmode="group",
        color_discrete_map=theme.GENDER_COLORS, text_auto=".2s",
    )
    fig_gender_hub.update_traces(cliponaxis=False)
    fig_gender_hub = theme.style_fig(
        fig_gender_hub, title="Average salary by hub and gender", height=360,
        legend_pos="top", tickangle=0, y_values=gender_hub["Salary"].tolist(), pad_frac=0.2,
    )
    fig_gender_hub.update_layout(xaxis_title="", yaxis_title="Avg salary (KES)")
    st.plotly_chart(fig_gender_hub, use_container_width=True, config={"displayModeBar": False}, key="salary_by_hub_gender_chart")

with s2:
    extremes_df = hub_pay.melt(id_vars=["Location"], value_vars=["Highest", "Lowest"], var_name="Boundary", value_name="Salary")
    fig_extremes = px.bar(
        extremes_df, x="Location", y="Salary", color="Boundary", barmode="group",
        color_discrete_map={"Highest": theme.NAVY, "Lowest": theme.TEAL}, text_auto=".2s",
    )
    fig_extremes.update_traces(cliponaxis=False)
    fig_extremes = theme.style_fig(
        fig_extremes, title="Pay ceiling vs. floor by hub", height=360,
        legend_pos="top", tickangle=0, y_values=extremes_df["Salary"].tolist(), pad_frac=0.2,
    )
    fig_extremes.update_layout(xaxis_title="", yaxis_title="Salary (KES)")
    st.plotly_chart(fig_extremes, use_container_width=True, config={"displayModeBar": False}, key="pay_ceiling_floor_chart")

with st.expander("See exact figures by hub"):
    display_hub_pay = hub_pay.copy()
    for c in ["Average", "Highest", "Lowest"]:
        display_hub_pay[c] = display_hub_pay[c].apply(lambda x: f"KES {x:,.0f}")
    st.dataframe(display_hub_pay, use_container_width=True, hide_index=True)

theme.signature()
