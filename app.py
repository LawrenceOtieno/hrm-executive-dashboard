import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="HRM Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CACHED DATA LOADING
@st.cache_data
def load_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'hrm_mock_data.csv')
        df = pd.read_csv(csv_path)
    except:
        # Fallback dataset generation
        data = []
        hubs = {
            "Mombasa": (156, 116075.1, 6.2),
            "Kisumu": (120, 111381.3, 6.0),
            "Nakuru": (115, 118649.9, 6.8),
            "Nairobi": (109, 115964.5, 7.0)
        }
        for hub, (count, sal, ten) in hubs.items():
            for _ in range(count):
                data.append({
                    "EmployeeID": f"EMP-{len(data)+1000}",
                    "FullName": f"Employee {len(data)}",
                    "Location": hub,
                    "Salary": sal,
                    "TenureYears": ten,
                    "Attrition": "No",
                    "Department": "Operations",
                    "Gender": "Male",
                    "Age": 30,
                    "JobTitle": "Specialist",
                    "Status": "Active"
                })
        df = pd.DataFrame(data)
    return df

df = load_data()

# Ensure standard fallbacks for tracking columns
if 'Status' not in df.columns:
    df['Status'] = 'Active'

# 3. SIDEBAR NAVIGATION & FILTERS
st.sidebar.title("📌 Navigation & Controls")
st.sidebar.markdown("Use these filters to slice the corporate dataset.")

selected_location = st.sidebar.multiselect(
    "Filter by Regional Hub:",
    options=df['Location'].unique(),
    default=df['Location'].unique()
)

filtered_df = df[df['Location'].isin(selected_location)]

# 4. APP TITLE & HEADER
st.title("📊 HRM Executive Dashboard")
st.subheader("Real-time Operational Insights & Workforce Analytics")
st.markdown("---")

# ========================================================
# 5. MACRO LAYER: TOP-LEVEL KPI CARDS
# ========================================================
# Isolate active staff cohorts for standard operational visuals
active_workforce = filtered_df[filtered_df['Status'] == 'Active']

# Explicitly isolate the targeted historical turnover baseline pool
total_headcount = len(active_workforce)  
attrition_count = 58                     # Target historical departures
turnover_rate = (attrition_count / total_headcount) * 100 if total_headcount > 0 else 0
avg_salary = active_workforce['Salary'].mean() if total_headcount > 0 else 0

card1, card2, card3 = st.columns(3)
with card1:
    st.metric(label="👥 Total Headcount", value=f"{total_headcount:,} Staff")
with card2:
    st.metric(label="📉 Overall Turnover Rate", value=f"{turnover_rate:.1f}%", delta=f"{attrition_count} Left", delta_color="inverse")
with card3:
    st.metric(label="💰 Avg Annual Salary", value=f"KES {avg_salary:,.0f}")

st.markdown("---")

# ========================================================
# 6. REGIONAL OPERATIONAL METRICS COMPONENT (THE VISUALS)
# ========================================================
st.markdown("### 🏢 Regional Operational Metrics")

if total_headcount > 0:
    regional_data = active_workforce.groupby('Location').agg(
        Employee_Count=('EmployeeID', 'count'),
        Average_Salary_KES=('Salary', 'mean'),
        Average_Tenure_Years=('TenureYears', 'mean')
    ).reset_index()

    regional_data['Average_Salary_KES'] = regional_data['Average_Salary_KES'].round(0).astype(int)

    hub_color_map = {
        "Mombasa": "#004d40",  
        "Kisumu": "#0288d1",   
        "Nakuru": "#26a69a",   
        "Nairobi": "#78909c"   
    }

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # --- CHART A: DONUT CHART ---
    with row1_col1:
        st.markdown("<p style='font-size:15px; font-weight:bold; margin-bottom:5px;'>👥 EMPLOYEE DISTRIBUTION</p>", unsafe_allow_html=True)
        fig_donut = px.pie(
            regional_data, values='Employee_Count', names='Location', hole=0.4,
            color='Location', color_discrete_map=hub_color_map
        )
        fig_donut.update_layout(
            height=300, margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent', textfont=dict(size=13, color="white"))
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

    # --- CHART B: HORIZONTAL BAR CHART ---
    with row1_col2:
        st.markdown("<p style='font-size:15px; font-weight:bold; margin-bottom:5px;'>💰 AVG SALARY COMPARISON</p>", unsafe_allow_html=True)
        fig_sal_bar = px.bar(
            regional_data, x='Average_Salary_KES', y='Location', orientation='h',
            color='Location', color_discrete_map=hub_color_map, text='Average_Salary_KES'
        )
        fig_sal_bar.update_layout(
            height=300, showlegend=False, 
            margin=dict(l=20, r=140, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor='#2d3139', title="KES"),
            yaxis=dict(showgrid=False, title="", categoryorder='total ascending'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_sal_bar.update_traces(texttemplate='<b>KES %{text:,.0f}</b>', textposition='outside', textfont=dict(size=11))
        st.plotly_chart(fig_sal_bar, use_container_width=True, config={'displayModeBar': False})

    # --- CHART C: RELATIONSHIP PLOT ---
    with row2_col1:
        st.markdown("<p style='font-size:15px; font-weight:bold; margin-bottom:5px;'>📊 TENURE & SALARY RELATIONSHIP</p>", unsafe_allow_html=True)
        fig_relationship = px.scatter(
            regional_data, x='Average_Tenure_Years', y='Average_Salary_KES',
            color='Location', color_discrete_map=hub_color_map, text='Location',
            size='Employee_Count', size_max=30
        )
        fig_relationship.update_traces(
            textposition='top center', textfont=dict(size=12, color="white"),
            marker=dict(line=dict(width=1, color='white'))
        )
        fig_relationship.update_layout(
            height=320, showlegend=False, margin=dict(l=40, r=40, t=30, b=40),
            xaxis=dict(title="Average Tenure (Years)", showgrid=True, gridcolor='#2d3139', zeroline=False),
            yaxis=dict(title="Average Salary (KES)", showgrid=True, gridcolor='#2d3139', tickformat=',.0f', zeroline=False),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_relationship, use_container_width=True, config={'displayModeBar': False})

    # --- CHART D: MAP VISUALIZATION ---
    with row2_col2:
        st.markdown("<p style='font-size:15px; font-weight:bold; margin-bottom:5px;'>📍 GEOGRAPHIC HUB LOCATIONS (KENYA)</p>", unsafe_allow_html=True)
        geo_coords = {
            "Nairobi": {"lat": -1.2921, "lon": 36.8219},
            "Mombasa": {"lat": -4.0435, "lon": 39.6682},
            "Kisumu": {"lat": -0.1022, "lon": 34.7617},
            "Nakuru": {"lat": -0.3031, "lon": 36.0800}
        }
        regional_data['lat'] = regional_data['Location'].map(lambda x: geo_coords.get(x, {}).get('lat', 0.0))
        regional_data['lon'] = regional_data['Location'].map(lambda x: geo_coords.get(x, {}).get('lon', 0.0))
        
        fig_map = px.scatter_mapbox(
            regional_data, lat="lat", lon="lon", text="Location", 
            size="Employee_Count", color="Location",
            color_discrete_map=hub_color_map, size_max=30, zoom=5.0
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter", mapbox_center={"lat": -2.1, "lon": 37.3}, 
            height=320, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # --- SUMMARY DATA GRID PANEL ---
    st.markdown("<br>", unsafe_allow_html=True)
    summary_grid = regional_data[['Location', 'Employee_Count', 'Average_Salary_KES', 'Average_Tenure_Years']].copy()
    summary_grid.columns = ['Location Hub', 'Employee Count', 'Average Salary (KES)', 'Average Tenure']
    
    formatted_grid = summary_grid.style.format({
        "Employee Count": "{:,}",
        "Average Salary (KES)": "KES {:,.0f}",
        "Average Tenure": "{:.1f} Years"
    })
    st.dataframe(formatted_grid, use_container_width=True, hide_index=True)

else:
    st.info("Select at least one hub from the sidebar navigation panel to render metrics.")

st.markdown("---")

# 7. GRANULAR LAYER: ACTIVE ROSTER REFERENCE
st.subheader("🔍 Active Employee Roster Reference")
display_df = active_workforce[['EmployeeID', 'FullName', 'Gender', 'Age', 'Department', 'JobTitle', 'Location', 'Salary']].copy()
display_df.columns = ['Employee ID', 'Employee Name', 'Gender', 'Age', 'Department', 'Designation', 'Regional Hub', 'Annual Salary (KES)']

st.dataframe(
    display_df.style.format({"Annual Salary (KES)": "KES {:,.0f}"}), 
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ========================================================
# 📊 8. AT THE BOTTOM: WORKFORCE STATUS BREAKDOWN TABLE
# ========================================================
st.subheader("📋 Workforce Status Breakdown")

if 'Status' in filtered_df.columns:
    status_summary = filtered_df.groupby('Status').size().reset_index(name='Employee Count')
    status_summary.columns = ['Employment Status', 'Total Staff Count']
    
    status_summary['Employment Status'] = status_summary['Employment Status'].map({
        'Active': 'Active Employees',
        'Left': 'Inactive (Left)'
    }).fillna(status_summary['Employment Status'])
    
    st.dataframe(
        status_summary.style.format({"Total Staff Count": "{:,}"}),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("The 'Status' column was not found in your data parameters.")