import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Departmental Insights", layout="wide")

st.title("🏢 Departmental Demographics & Compensation Analysis")
st.markdown("Deep-dive evaluation of gender distributions, age profiles, compensation benchmarks, and attrition patterns across corporate departments.")

# 2. PATH RESOLVER & CACHED DATA LOADING
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

# Ensure standard fallbacks for status tracking
if 'Status' not in df.columns:
    df['Status'] = 'Active'

# --- DYNAMIC COLUMN CHECKER ---
columns = list(df.columns)

# 1. Detect Location Column
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

# 2. Detect Salary Column
salary_col = None
for col in ['Annual Salary', 'Salary', 'annual_salary', 'salary', 'Base Salary']:
    if col in columns:
        salary_col = col
        break
if not salary_col:
    for col in columns:
        if 'sal' in col.lower():
            salary_col = col
            break
    if not salary_col:
        salary_col = columns[1]

# --- REUSABLE COMPONENT: Sidebar Filter ---
st.sidebar.header("Filter Options")
all_hubs = sorted(df[loc_col].unique())
selected_hubs = st.sidebar.multiselect(f"Filter by {loc_col}:", all_hubs, default=all_hubs)

# Filter global dataset based on selected hub locations
filtered_df = df[df[loc_col].isin(selected_hubs)]

# Split dataset into Active and Left cohorts to keep calculations mathematically consistent
active_df = filtered_df[filtered_df['Status'] == 'Active']
left_df = filtered_df[filtered_df['Status'] == 'Left']

# ==========================================
# 📊 SECTION 1: GENDER DISTRIBUTION BY DEPT
# ==========================================
st.header("1. Gender Distribution Across Departments")

if not active_df.empty:
    gender_dept = active_df.groupby(['Department', 'Gender']).size().reset_index(name='Employee Count')

    fig_gender = px.bar(
        gender_dept,
        x='Department',
        y='Employee Count',
        color='Gender',
        barmode='group',
        title="Active Staff Headcount by Department & Gender",
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
# 👶 NEW SECTION 2: AGE PROFILE ANALYSIS
# ==========================================
st.header("2. Departmental Age Distribution Profiles")

if not active_df.empty and 'Age' in active_df.columns:
    # Create distinct operational age bands using Pandas cut
    age_bins = [0, 29, 39, 49, 100]
    age_labels = ['Under 30', '30–39 Years', '40–49 Years', '50+ Years']
    
    # Use .loc to avoid Slice Copy setting alerts
    active_analysis = active_df.copy()
    active_analysis['Age Group'] = pd.cut(active_analysis['Age'], bins=age_bins, labels=age_labels)
    
    age_dept_summary = active_analysis.groupby(['Department', 'Age Group'], observed=False).size().reset_index(name='Staff Count')
    
    fig_age = px.bar(
        age_dept_summary,
        x='Department',
        y='Staff Count',
        color='Age Group',
        title="Active Workforce Age Cohorts by Department",
        color_discrete_sequence=px.colors.sequential.YlGnBu_r,
        barmode='stack',
        text_auto=True
    )
    fig_age.update_layout(xaxis_title="Department", yaxis_title="Active Employees", legend_title="Age Brackets")
    st.plotly_chart(fig_age, use_container_width=True)
else:
    st.warning("Age data fields are unavailable or selection pool is empty.")

st.markdown("---")

# ==========================================
# 💰 SECTION 3: HIGHEST & LOWEST SALARIES
# ==========================================
st.header("3. Departmental Salary Benchmarks")

if not active_df.empty:
    salary_dept = active_df.groupby('Department')[salary_col].mean().reset_index()
    salary_dept = salary_dept.sort_values(by=salary_col, ascending=False)

    fig_salary = px.bar(
        salary_dept,
        x=salary_col,
        y='Department',
        orientation='h',
        title=f"Average {salary_col} Segment by Department (KES)",
        color=salary_col,
        color_continuous_scale=px.colors.sequential.GnBu, 
        text_auto='.2s'
    )
    fig_salary.update_layout(xaxis_title=f"Average {salary_col} (KES)", yaxis_title="Department", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_salary, use_container_width=True)

    st.subheader("📋 Granular Salary Summary Table")
    salary_summary_table = active_df.groupby('Department').agg(
        Highest_Salary=(salary_col, 'max'),
        Average_Salary=(salary_col, 'mean'),
        Lowest_Salary=(salary_col, 'min')
    ).reset_index()

    formatted_table = salary_summary_table.copy()
    for col in ['Highest_Salary', 'Average_Salary', 'Lowest_Salary']:
        formatted_table[col] = formatted_table[col].apply(lambda x: f"KES {x:,.0f}")

    st.dataframe(formatted_table, use_container_width=True, hide_index=True)
else:
    st.warning("Please select at least one filter option to display compensation insights.")

st.markdown("---")

# ==========================================
# 🛑 NEW SECTION 4: DEPARTURES BY DEPARTMENT
# ==========================================
st.header("4. Corporate Attrition Distribution Analysis")

if not left_df.empty:
    # Compile exactly how many of the 58 staff members left per department
    attrition_dept = left_df.groupby('Department').size().reset_index(name='Departures Count')
    attrition_dept = attrition_dept.sort_values(by='Departures Count', ascending=False)
    
    # Calculate global contextual metrics
    total_departures_shown = attrition_dept['Departures Count'].sum()
    
    st.markdown(f"**Historical Turnover Tracking:** Showing **{total_departures_shown} Total Departures** matching your sidebar geography choices.")
    
    fig_attrition = px.bar(
        attrition_dept,
        x='Departures Count',
        y='Department',
        orientation='h',
        title="Historical Attrition Volume by Corporate Department",
        color='Departures Count',
        color_continuous_scale=px.colors.sequential.OrRd,
        text_auto=True
    )
    fig_attrition.update_layout(
        xaxis_title="Number of Departed Employees", 
        yaxis_title="Department",
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_attrition, use_container_width=True)
    
    # Render detailed data summary frame for audit purposes
    st.subheader("📋 Turnover Count by Department")
    st.dataframe(
        attrition_dept.style.format({"Departures Count": "{:,}"}),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No employee departure records match your selected regional filter options.")