import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import theme

st.set_page_config(page_title="Regional Pay Equity", layout="wide")
theme.inject_css()

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

overall_gap = (
    (active_df.groupby("Gender")["Salary"].mean()["Male"] - active_df.groupby("Gender")["Salary"].mean()["Female"])
    / active_df.groupby("Gender")["Salary"].mean()["Female"] * 100
)

st.markdown("---")
k1, k2, k3 = st.columns(3)
with k1:
    theme.kpi_card("Highest-Paying Hub", hub_pay.iloc[0]["Location"], f"KES {hub_pay.iloc[0]['Average']:,.0f} avg")
with k2:
    theme.kpi_card("Lowest-Paying Hub", hub_pay.iloc[-1]["Location"], f"KES {hub_pay.iloc[-1]['Average']:,.0f} avg")
with k3:
    theme.kpi_card(
        "Company-wide Gender Pay Gap", f"{overall_gap:.1f}%", "Men vs. women, average annual salary",
        tone="alert" if overall_gap > 3 else "good",
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
fig_hero.update_traces(texttemplate="KES %{text:,.0f}", textposition="inside", textfont_color=theme.WHITE)
fig_hero = theme.style_fig(fig_hero, height=300, legend=False)
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
    st.markdown("**Average salary by hub and gender**")
    gender_hub = active_df.groupby(["Location", "Gender"])["Salary"].mean().reset_index()
    fig_gender_hub = px.bar(
        gender_hub, x="Location", y="Salary", color="Gender", barmode="group",
        color_discrete_map=theme.GENDER_COLORS, text_auto=".2s",
    )
    fig_gender_hub = theme.style_fig(fig_gender_hub, height=300)
    fig_gender_hub.update_layout(xaxis_title="", yaxis_title="Avg salary (KES)")
    st.plotly_chart(fig_gender_hub, use_container_width=True, config={"displayModeBar": False})

with s2:
    st.markdown("**Pay ceiling vs. floor by hub**")
    extremes_df = hub_pay.melt(id_vars=["Location"], value_vars=["Highest", "Lowest"], var_name="Boundary", value_name="Salary")
    fig_extremes = px.bar(
        extremes_df, x="Location", y="Salary", color="Boundary", barmode="group",
        color_discrete_map={"Highest": theme.NAVY, "Lowest": theme.TEAL}, text_auto=".2s",
    )
    fig_extremes = theme.style_fig(fig_extremes, height=300)
    fig_extremes.update_layout(xaxis_title="", yaxis_title="Salary (KES)")
    st.plotly_chart(fig_extremes, use_container_width=True, config={"displayModeBar": False})

with st.expander("See exact figures by hub"):
    display_hub_pay = hub_pay.copy()
    for c in ["Average", "Highest", "Lowest"]:
        display_hub_pay[c] = display_hub_pay[c].apply(lambda x: f"KES {x:,.0f}")
    st.dataframe(display_hub_pay, use_container_width=True, hide_index=True)

theme.signature()
