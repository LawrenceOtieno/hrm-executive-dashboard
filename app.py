import streamlit as st

st.set_page_config(
    page_title="HRM Executive Dashboard",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg_glance = st.Page("pages/0_At_a_Glance.py", title="📊 At a Glance", default=True)
pg_story = st.Page("pages/1_The_Story.py", title="🧭 The Story")
pg_attrition = st.Page("pages/2_Who_Is_Leaving.py", title="📉 Who's Leaving & Why")
pg_dept = st.Page("pages/3_Departmental_Insights.py", title="🏢 Departmental Insights")
pg_regional = st.Page("pages/4_Regional_Pay_Equity.py", title="📍 Regional Pay Equity")

pg = st.navigation([pg_glance, pg_story, pg_attrition, pg_dept, pg_regional])
pg.run()
