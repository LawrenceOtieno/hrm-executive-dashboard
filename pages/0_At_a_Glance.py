import sys
import os
import datetime
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
avg_salary = active["Salary"].mean()
gap_pct, gap_higher = theme.gender_pay_gap(active)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("<div class='section-kicker'>Single-Screen Overview</div>", unsafe_allow_html=True)
    st.title("📊 At a Glance")
    st.markdown(
        "Every headline number and chart on one screen. Head to **The Story** for the "
        "narrative behind these numbers, with drill-down into individual records."
    )
with h2:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    st.caption(f"Snapshot as of {datetime.date.today().strftime('%d %b %Y')}")
    st.caption(f"{total_headcount + total_departures} employee records")

st.markdown("---")

# ---------------------------------------------------------------------------
# DOWNLOAD & SHARE
# ---------------------------------------------------------------------------
with st.expander("⬇️ Download & share this dashboard", expanded=False):
    st.caption(
        "Share a single file that visually summarizes this analysis — no need to send "
        "someone a link to the live app."
    )
    export_fig = theme.build_export_dashboard(df)
    d1, d2 = st.columns(2)

    with d1:
        html_bytes = export_fig.to_html(include_plotlyjs=True, full_html=True).encode("utf-8")
        st.download_button(
            "📄 Download as HTML (recommended)",
            data=html_bytes,
            file_name="hrm_dashboard_at_a_glance.html",
            mime="text/html",
            use_container_width=True,
            help="Opens in any browser, fully self-contained, and stays interactive (hover for exact values). Works on every machine.",
        )

    with d2:
        try:
            png_bytes = export_fig.to_image(format="png", scale=2)
            st.download_button(
                "🖼️ Download as PNG image",
                data=png_bytes,
                file_name="hrm_dashboard_at_a_glance.png",
                mime="image/png",
                use_container_width=True,
                help="A flat image — easiest to drop into a slide, email, or Slack message.",
            )
        except Exception:
            st.button("🖼️ Download as PNG image", disabled=True, use_container_width=True)
            st.caption(
                "PNG export needs Google Chrome installed on this machine (used behind the "
                "scenes to render the image) — it isn't available here. The HTML download "
                "on the left works everywhere and needs no extra setup."
            )

st.markdown("---")

# ---------------------------------------------------------------------------
# KPI STRIP (5 tiles)
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    theme.mini_kpi_card("Headcount", f"{total_headcount:,}")
with k2:
    theme.mini_kpi_card("Turnover", f"{turnover_rate:.1f}%", tone="alert")
with k3:
    theme.mini_kpi_card("Involuntary Exits", f"{involuntary_share:.0f}%", tone="alert")
with k4:
    theme.mini_kpi_card("Avg Annual Salary", f"KES {avg_salary/1_000_000:.2f}M")
with k5:
    theme.mini_kpi_card(
        "Gender Pay Gap", f"{gap_pct:.1f}%", tone="alert" if gap_pct > 3 else "good"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TILE GRID — 4 columns x 2 rows, each tile in a bordered card for a clean
# Power BI-style canvas. No drill-down here on purpose -- this page is a
# fast scan, not a workspace (that's what the other pages are for).
# ---------------------------------------------------------------------------
row1 = st.columns(4)
row2 = st.columns(4)

# --- Tile 1: Turnover by department ---
with row1[0]:
    with st.container(border=True):
        dept_summary = df.groupby("Department")["Status"].value_counts().unstack(fill_value=0)
        dept_summary["Total"] = dept_summary.sum(axis=1)
        dept_summary["TurnoverRate"] = (dept_summary.get("Left", 0) / dept_summary["Total"] * 100).round(1)
        dept_summary = dept_summary.reset_index().sort_values("TurnoverRate")
        fig = px.bar(
            dept_summary, x="TurnoverRate", y="Department", orientation="h",
            color="TurnoverRate", color_continuous_scale=[theme.TEAL, theme.NAVY_LIGHT, theme.ORANGE, theme.ORANGE_DARK],
        )
        fig.update_coloraxes(showscale=False)
        fig = theme.style_mini_fig(fig, title="Turnover % by Dept")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_dept_turnover")

# --- Tile 2: Turnover by hub ---
with row1[1]:
    with st.container(border=True):
        hub_summary = df.groupby("Location")["Status"].value_counts().unstack(fill_value=0)
        hub_summary["Total"] = hub_summary.sum(axis=1)
        hub_summary["TurnoverRate"] = (hub_summary.get("Left", 0) / hub_summary["Total"] * 100).round(1)
        hub_summary = hub_summary.reset_index().sort_values("TurnoverRate")
        fig = px.bar(
            hub_summary, x="TurnoverRate", y="Location", orientation="h",
            color="Location", color_discrete_map=theme.HUB_COLORS,
        )
        fig = theme.style_mini_fig(fig, title="Turnover % by Hub")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_hub_turnover")

# --- Tile 3: Gender split ---
with row1[2]:
    with st.container(border=True):
        gender_split = active["Gender"].value_counts().reset_index()
        gender_split.columns = ["Gender", "Count"]
        fig = px.pie(
            gender_split, values="Count", names="Gender", hole=0.55,
            color="Gender", color_discrete_map=theme.GENDER_COLORS,
        )
        fig.update_traces(textinfo="percent", textfont=dict(size=10, color=theme.WHITE))
        fig = theme.style_mini_fig(fig, title="Gender Split")
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_gender_split")

# --- Tile 4: Exit type split ---
with row1[3]:
    with st.container(border=True):
        term_split = left["TerminationType"].value_counts().reset_index()
        term_split.columns = ["TerminationType", "Count"]
        fig = px.pie(
            term_split, values="Count", names="TerminationType", hole=0.55,
            color="TerminationType", color_discrete_map=theme.TERMINATION_COLORS,
        )
        fig.update_traces(textinfo="percent", textfont=dict(size=10, color=theme.WHITE))
        fig = theme.style_mini_fig(fig, title="Exit Type")
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_exit_type")

# --- Tile 5: Avg salary by hub ---
with row2[0]:
    with st.container(border=True):
        hub_pay = active.groupby("Location")["Salary"].mean().reset_index().sort_values("Salary")
        fig = px.bar(
            hub_pay, x="Salary", y="Location", orientation="h",
            color="Location", color_discrete_map=theme.HUB_COLORS,
        )
        fig = theme.style_mini_fig(fig, title="Avg Salary by Hub")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_salary_hub")

# --- Tile 6: Avg salary by department ---
with row2[1]:
    with st.container(border=True):
        dept_pay = active.groupby("Department")["Salary"].mean().reset_index().sort_values("Salary")
        fig = px.bar(
            dept_pay, x="Salary", y="Department", orientation="h",
            color="Salary", color_continuous_scale=[theme.TEAL, theme.NAVY_LIGHT, theme.NAVY],
        )
        fig.update_coloraxes(showscale=False)
        fig = theme.style_mini_fig(fig, title="Avg Salary by Dept")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_salary_dept")

# --- Tile 7: Age bands ---
with row2[2]:
    with st.container(border=True):
        age_bins = [0, 29, 39, 49, 100]
        age_labels = ["Under 30", "30-39", "40-49", "50+"]
        age_df = active.copy()
        age_df["Age Group"] = pd.cut(age_df["Age"], bins=age_bins, labels=age_labels)
        age_counts = age_df["Age Group"].value_counts().reindex(age_labels).reset_index()
        age_counts.columns = ["Age Group", "Count"]
        fig = px.bar(
            age_counts, x="Age Group", y="Count", color="Age Group",
            color_discrete_sequence=theme.DEPT_COLOR_SEQUENCE,
        )
        fig = theme.style_mini_fig(fig, title="Active Age Bands")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_age_bands")

# --- Tile 8: Headcount by department ---
with row2[3]:
    with st.container(border=True):
        dept_headcount = active["Department"].value_counts().reset_index()
        dept_headcount.columns = ["Department", "Count"]
        dept_headcount = dept_headcount.sort_values("Count")
        fig = px.bar(
            dept_headcount, x="Count", y="Department", orientation="h",
            color="Department", color_discrete_sequence=theme.DEPT_COLOR_SEQUENCE,
        )
        fig = theme.style_mini_fig(fig, title="Headcount by Dept")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="glance_headcount_dept")

theme.signature()
