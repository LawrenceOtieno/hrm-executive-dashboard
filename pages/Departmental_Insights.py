import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Departmental Insights", layout="wide")

st.title("🏢 Departmental Demographics & Compensation Analysis")
st.markdown("Deep-dive evaluation of gender distributions and salary benchmarks across corporate departments.")

# 2. Robust Multi-Page Path Resolver
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
# This automatically maps column names to prevent KeyErrors
columns = list(df.columns)

# 1. Detect Location Column
loc_col = None
for col in ['Location Hub', 'Location', 'location_hub', 'hub', 'Hub']:
    if col in columns:
        loc_col = col
        break
if not loc_col:
    # Fallback to the first column containing 'loc' or 'hub' if no exact match
    for col in columns:
        if 'loc' in col.lower() or 'hub' in col.lower():
            loc_col = col
            break
    if not loc_col:
        loc_col = columns[0] # Default fallback

# --- REUSABLE COMPONENT: Sidebar Filter ---
st.sidebar.header("Filter Options")
all_hubs = sorted(df[loc_col].unique())
selected_hubs = st.sidebar.multiselect(f"Filter by {loc_col}:", all_hubs, default=all_hubs)

# Filter dataset based on selection
filtered_df = df[df[loc_col].isin(selected_hubs)]

# ==========================================
# 📊 SECTION 1: GENDER DISTRIBUTION BY DEPT
# ==========================================
st.header("1. Gender Distribution Across Departments")

if not filtered_df.empty:
    gender_dept = filtered_df.groupby(['Department', 'Gender']).size().reset_index(name='Employee Count')

    fig_gender = px.bar(
        gender_dept,
        x='Department',
        y='Employee Count',
        color='Gender',
        barmode='group',
        title="Staff Headcount by Department & Gender",
        color_discrete_map={'Female': '#0288d1', 'Male': '#004c6d'}, 
        text_auto=True
    )
    fig_gender.update_layout(xaxis_title="Department", yaxis_title="Number of Employees")
    st.plotly_chart(fig_gender, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        female_df = gender_dept[gender_dept['Gender'] == 'Female']
        if not female_df.empty:
            top_female_dept = female_df.loc[female_df['Employee Count'].idxmax()]
            st.metric(
                label="Highest Female Representation", 
                value=top_female_dept['Department'], 
                delta=f"{top_female_dept['Employee Count']} Women"
            )
    with col2:
        male_df = gender_dept[gender_dept['Gender'] == 'Male']
        if not male_df.empty:
            top_male_dept = male_df.loc[male_df['Employee Count'].idxmax()]
            st.metric(
                label="Highest Male Representation", 
                value=top_male_dept['Department'], 
                delta=f"{top_male_dept['Employee Count']} Men"
            )
else:
    st.warning("Please select at least one filter option to display gender metrics.")

st.markdown("---")

# ==========================================
# 💰 SECTION 2: HIGHEST & LOWEST SALARIES
# ==========================================
st.header("2. Departmental Salary Benchmarks")

if not filtered_df.empty:
    salary_dept = filtered_df.groupby('Department')['Annual Salary'].mean().reset_index()
    salary_dept = salary_dept.sort_values(by='Annual Salary', ascending=False)

    fig_salary = px.bar(
        salary_dept,
        x='Annual Salary',
        y='Department',
        orientation='h',
        title="Average Annual Salary Segment by Department (KES)",
        color='Annual Salary',
        color_continuous_scale=px.colors.sequential.GnBu, 
        text_auto='.2s'
    )
    fig_salary.update_layout(xaxis_title="Average Salary (KES)", yaxis_title="Department", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_salary, use_container_width=True)

    st.subheader("📋 Granular Salary Summary Table")
    salary_summary_table = filtered_df.groupby('Department').agg(
        Highest_Salary=('Annual Salary', 'max'),
        Average_Salary=('Annual Salary', 'mean'),
        Lowest_Salary=('Annual Salary', 'min')
    ).reset_index()

    formatted_table = salary_summary_table.copy()
    for col in ['Highest_Salary', 'Average_Salary', 'Lowest_Salary']:
        formatted_table[col] = formatted_table[col].apply(lambda x: f"KES {x:,.2f}")

    st.dataframe(formatted_table, use_container_width=True, hide_index=True)
else:
    st.warning("Please select at least one filter option to display compensation insights.")