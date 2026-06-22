import streamlit as st

# Define multi-page structure cleanly without execution wrappers
pg_main = st.Page("HRM_General_app.py", title="?? HRM General", default=True)
pg_dept = st.Page("pages/Departmental_Insights.py", title="?? Departmental Insights")
pg_regional = st.Page("pages/Regional_Pay_Analysis.py", title="?? Regional Pay Analysis")

pg = st.navigation([pg_main, pg_dept, pg_regional])
pg.run()
