import streamlit as st

# Define your multi-page layout cleanly using separate target scripts
pg_main = st.Page("pages/HRM_General_app.py", title="📊 HRM General", default=True)
pg_dept = st.Page("pages/Departmental_Insights.py", title="🏢 Departmental Insights")
pg_regional = st.Page("pages/Regional_Pay_Analysis.py", title="📍 Regional Pay Analysis")

# Run navigation smoothly without element collisions
pg = st.navigation([pg_main, pg_dept, pg_regional])
pg.run()