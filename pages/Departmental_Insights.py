import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Departmental Insights", layout="wide")

st.title("🏢 Departmental Demographics & Compensation Analysis")
st.markdown("Deep-dive evaluation of gender distributions and salary benchmarks across corporate departments.")

# 2. Load Data (Using st.cache_data so it stays lightning fast)
@st.cache_data
def load_data():
    # Replace this path with your actual dataset file path if different
    df = pd.read_csv("data/hrm_v2_dataset.csv") 
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Could not load the dataset. Please verify the file path.")
    st.stop()

# --- REUSABLE COMPONENT: Sidebar Filter ---
st.sidebar.header("Filter Options")
all_hubs = sorted(df['Location Hub'].unique())
selected_hubs = st.sidebar.multiselect("Filter by Regional Hub:", all_hubs, default=all_hubs)

# Filter dataset based on selection
filtered_df = df[df['Location Hub'].isin(selected_hubs)]

# ==========================================
# 📊 QUESTION 1: GENDER DISTRIBUTION BY DEPT
# ==========================================
st.header("1. Gender Distribution Across Departments")

# Aggregate data to count males and females per department
gender_dept = filtered_df.groupby(['Department', 'Gender']).size().reset_index(name='Employee Count')

# Create a grouped or stacked bar chart
fig_gender = px.bar(
    gender_dept,
    x='Department',
    y='Employee Count',
    color='Gender',
    barmode='group',
    title="Staff Headcount by Department & Gender",
    color_discrete_map={'Female': '#0288d1', 'Male': '#004c6d'}, # Keeping your clean theme colors
    text_auto=True
)
fig_gender.update_layout(xaxis_title="Department", yaxis_title="Number of Employees")
st.plotly_chart(fig_gender, use_container_width=True)

# Add a quick metric Callout for the Executive
col1, col2 = st.columns(2)
with col1:
    # Find top female department
    female_df = gender_dept[gender_dept['Gender'] == 'Female']
    if not female_df.empty:
        top_female_dept = female_df.loc[female_df['Employee Count'].idxmax()]
        st.metric(
            label="Highest Female Representation", 
            value=top_female_dept['Department'], 
            delta=f"{top_female_dept['Employee Count']} Women"
        )
with col2:
    # Find top male department
    male_df = gender_dept[gender_dept['Gender'] == 'Male']
    if not male_df.empty:
        top_male_dept = male_df.loc[male_df['Employee Count'].idxmax()]
        st.metric(
            label="Highest Male Representation", 
            value=top_male_dept['Department'], 
            delta=f"{top_male_dept['Employee Count']} Men"
        )

st.markdown("---")

# ==========================================
# 💰 QUESTION 2: HIGHEST & LOWEST SALARIES
# ==========================================
st.header("2. Departmental Salary Benchmarks")

# Calculate average salary per department
salary_dept = filtered_df.groupby('Department')['Annual Salary'].mean().reset_index()
salary_dept = salary_dept.sort_values(by='Annual Salary', ascending=False)

# Create a horizontal bar chart to showcase rankings cleanly
fig_salary = px.bar(
    salary_dept,
    x='Annual Salary',
    y='Department',
    orientation='h',
    title="Average Annual Salary Segment by Department (KES)",
    color='Annual Salary',
    color_continuous_scale=px.colors.sequential.GnBu, # Clean blue-green scale matching your UI
    text_auto='.2s'
)
fig_salary.update_layout(xaxis_title="Average Salary (KES)", yaxis_title="Department", yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_salary, use_container_width=True)

# Detailed Table breakdown for the summary layer
st.subheader("📋 Granular Salary Summary Table")
salary_summary_table = filtered_df.groupby('Department').agg(
    Highest_Salary=('Annual Salary', 'max'),
    Average_Salary=('Annual Salary', 'mean'),
    Lowest_Salary=('Annual Salary', 'min')
).reset_index()

# Format numbers nicely as KES
for col in ['Highest_Salary', 'Average_Salary', 'Lowest_Salary']:
    salary_summary_table[col] = salary_summary_table[col].apply(lambda x: f"KES {x:,.2f}")

st.dataframe(salary_summary_table, use_container_width=True, hide_index=True)