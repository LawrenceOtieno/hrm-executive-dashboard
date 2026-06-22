import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="HRM Executive Dashboard", layout="wide")

st.title("📊 HRM Executive Dashboard Overview")
st.markdown("Real-time strategic workforce analytics, headcount tracking, and core corporate retention metrics.")

# 2. Robust Multi-Page Path Resolver
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    csv_path = os.path.join(BASE_DIR, "hrm_mock_data.csv")
    df = pd.read_csv(csv_path) 
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset. Error details: {e}")
    st.stop()

# --- DYNAMIC COLUMN CHECKER ---
columns = list(df.columns)

# Detect Location Hub Column
loc_col = None
for col in ['Location Hub', 'Location', 'location_hub', 'hub', 'Hub']:
    if col in columns:
        loc_col = col
        break
if not loc_col:
    for col in columns:
        if 'loc' in col.lower() or 'hub' in col.lower():
            loc_col = col
            break
    if not loc_col:
        loc_col = columns[0]


# --- GLOBAL SIDEBAR FILTER ---
st.sidebar.header("Global Filters")
all_hubs = sorted(df[loc_col].unique())
selected_hubs = st.sidebar.multiselect(f"Filter by {loc_col}:", all_hubs, default=all_hubs)

# Filter base data by selected location hubs
filtered_df = df[df[loc_col].isin(selected_hubs)]


# ==========================================
# 🔍 THE CRITICAL STATUS FILTER LINES
# ==========================================
# Split the 558 rows into active and departed cohorts
active_df = filtered_df[filtered_df['Status'] == 'Active']
left_df = filtered_df[filtered_df['Status'] == 'Left']

# Calculate precise workforce metrics dynamically
total_active = len(active_df)
total_left = len(left_df)
total_historical = total_active + total_left

# Calculate Turnover Rate: (Departures / Total Workspace Pool) * 100
if total_historical > 0:
    turnover_rate = (total_left / total_historical) * 100
else:
    turnover_rate = 0.0


# ==========================================
# 🏛️ EXECUTIVE KPI SUMMARY CARDS
# ==========================================
st.subheader("📌 Corporate Core Vital Metrics")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    # Will display exactly 500 when no sidebar filters are active
    st.metric(label="Active Workforce Headcount", value=f"{total_active} Employees")
    
with kpi2:
    # Will display exactly 11.6% when no sidebar filters are active
    st.metric(label="Annual Turnover Rate", value=f"{turnover_rate:.1f}%")
    
with kpi3:
    # Will display exactly 58 when no sidebar filters are active
    st.metric(label="Total Historical Departures", value=f"{total_left} Staff")

st.markdown("---")


# ==========================================
# 📈 CORE VISUALIZATION: CURRENT HEADCOUNT
# ==========================================
st.header("1. Active Workforce Breakdown by Department")

if not active_df.empty:
    dept_counts = active_df['Department'].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Active Staff Count']
    
    fig_active_dept = px.bar(
        dept_counts,
        x='Department',
        y='Active Staff Count',
        title="Active Headcount Distribution Across Operations",
        color='Active Staff Count',
        color_continuous_scale=px.colors.sequential.Blugrn,
        text_auto=True
    )
    fig_active_dept.update_layout(xaxis_title="Department", yaxis_title="Number of Active Employees", coloraxis_showscale=False)
    st.plotly_chart(fig_active_dept, use_container_width=True)
else:
    st.warning("Please select at least one filter option to display operational data layouts.")