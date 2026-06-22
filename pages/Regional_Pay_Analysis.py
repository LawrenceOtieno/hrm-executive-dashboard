import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Regional Pay Analysis", layout="wide")

st.title("📍 Regional Pay & Compensation Benchmarking")
st.markdown("Comparative analysis identifying geographic salary variations, highest-paid hubs, and structural pay extremes.")

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

# Ensure standard fallbacks for tracking columns
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
    loc_col = columns[0]

# 2. Detect Salary Column
salary_col = None
for col in ['Annual Salary', 'Salary', 'annual_salary', 'salary', 'Base Salary']:
    if col in columns:
        salary_col = col
        break
if not salary_col:
    salary_col = columns[1]

# Filter strictly for active personnel for live compensation benchmarking
active_df = df[df['Status'] == 'Active']

# ==========================================
# 💰 SECTION 1: MACRO BENCHMARKS BY HUB
# ==========================================
st.header("1. Average Salary Rankings by Regional Hub")

if not active_df.empty:
    # Group by region to calculate metrics
    hub_pay = active_df.groupby(loc_col)[salary_col].agg(['mean', 'max', 'min']).reset_index()
    hub_pay.columns = ['Region', 'Average Salary', 'Highest Salary', 'Lowest Salary']
    hub_pay = hub_pay.sort_values(by='Average Salary', ascending=False)

    # Color palette matching your original hub color profile
    hub_color_map = {
        "Mombasa": "#004d40",  
        "Kisumu": "#0288d1",   
        "Nakuru": "#26a69a",   
        "Nairobi": "#78909c"   
    }

    # Generate custom labels to force '110k+' style text string on the visual
    hub_pay['Display_Label'] = hub_pay['Average Salary'].apply(
        lambda val: "110k+" if val >= 110000 else f"{val/1000:.0f}k"
    )

    # Chart: Average Salary Comparison
    fig_avg = px.bar(
        hub_pay,
        x='Average Salary',
        y='Region',
        orientation='h',
        title="Ranked Average Base Compensation by Hub (KES)",
        color='Region',
        color_discrete_map=hub_color_map,
        text='Display_Label'  # Use our explicit custom label column
    )
    fig_avg.update_layout(
        xaxis_title="Average Salary (KES)", 
        yaxis_title="Regional Hub", 
        showlegend=False
    )
    # Style text inside bars to make it clean and visible
    fig_avg.update_traces(textposition='inside', textfont=dict(size=12, color='white'))
    st.plotly_chart(fig_avg, use_container_width=True)

    # Display Top-Level Metrics for Highest and Lowest Paying Regions
    highest_paying_hub = hub_pay.iloc[0]
    lowest_paying_hub = hub_pay.iloc[-1]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Highest Average Paying Hub",
            value=highest_paying_hub['Region'],
            delta=f"KES {highest_paying_hub['Average Salary']:,.0f} Avg"
        )
    with col2:
        st.metric(
            label="Lowest Average Paying Hub",
            value=lowest_paying_hub['Region'],
            delta=f"KES {lowest_paying_hub['Average Salary']:,.0f} Avg",
            delta_color="inverse"
        )
else:
    st.warning("No active employee metrics found.")

st.markdown("---")

# ==========================================
# 📊 SECTION 2: REGIONAL COMPENSATION EXTREMES
# ==========================================
st.header("2. Salary Extremes: Highest vs. Lowest Pays Within Each Region")

if not active_df.empty:
    # Melt the dataframe to compare Max and Min easily side-by-side
    extremes_df = hub_pay.melt(id_vars=['Region'], value_vars=['Highest Salary', 'Lowest Salary'], 
                               var_name='Pay Boundary', value_name='Salary Value')

    fig_extremes = px.bar(
        extremes_df,
        x='Region',
        y='Salary Value',
        color='Pay Boundary',
        barmode='group',
        title="Compensation Spans: Top Earner vs Bottom Earner Ceilings by Location",
        color_discrete_map={'Highest Salary': '#004c6d', 'Lowest Salary': '#26a69a'},
        text_auto='.2s'
    )
    fig_extremes.update_layout(xaxis_title="Regional Hub", yaxis_title="Compensation Boundary (KES)")
    st.plotly_chart(fig_extremes, use_container_width=True)
    
    # Grid Data Layout Panel
    st.subheader("📋 Regional Salary Boundaries Table")
    formatted_hub_pay = hub_pay.copy()
    for col in ['Average Salary', 'Highest Salary', 'Lowest Salary']:
        formatted_hub_pay[col] = formatted_hub_pay[col].apply(lambda x: f"KES {x:,.0f}")
        
    st.dataframe(formatted_hub_pay[['Region', 'Average Salary', 'Highest Salary', 'Lowest Salary']], use_container_width=True, hide_index=True)
    
st.markdown("---")

# ==========================================
# 🔍 SECTION 3: TOP & BOTTOM EARNERS ROSTER
# ==========================================
st.header("3. Compensation Extreme Audit Roster")
st.markdown("Select an investment hub to review specific team member records sitting at the extreme edges of the compensation bracket.")

selected_hub = st.selectbox("Select Regional Hub for Payroll Audit:", options=sorted(active_df[loc_col].unique()))

if selected_hub:
    hub_specific_df = active_df[active_df[loc_col] == selected_hub]
    
    # Extract Max and Min boundary rows for the selected hub
    max_salary = hub_specific_df[salary_col].max()
    min_salary = hub_specific_df[salary_col].min()
    
    extremes_roster = hub_specific_df[(hub_specific_df[salary_col] == max_salary) | (hub_specific_df[salary_col] == min_salary)].copy()
    
    # Create an auditing tier flag
    extremes_roster['Pay Tier Bracket'] = extremes_roster[salary_col].apply(
        lambda x: "📈 Top Earner Bracket" if x == max_salary else "📉 Bottom Earner Bracket"
    )
    
    # Organize columns cleanly
    display_cols = ['Pay Tier Bracket', 'EmployeeID', 'FullName', 'Department', 'JobTitle', salary_col]
    available_cols = [c for c in display_cols if c in extremes_roster.columns]
    
    final_roster = extremes_roster[available_cols].sort_values(by=salary_col, ascending=False)
    
    st.dataframe(
        final_roster.style.format({salary_col: "KES {:,.0f}"}),
        use_container_width=True,
        hide_index=True
    )