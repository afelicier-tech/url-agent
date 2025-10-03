# review_app.py
import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("url_checks.db", check_same_thread=False)

st.title("URL Agent - Review Dashboard")
df = pd.read_sql_query("SELECT id, url, final_url, status_code, ok, redirects, latency_ms, content_type, error, created_at FROM url_checks ORDER BY created_at DESC", conn)
st.dataframe(df)

if st.button("Re-run failing (status>=400)"):
    failing = df[df['status_code'] >= 400]['url'].tolist()
    st.write("Re-running:", len(failing))
    import subprocess, sys
    if failing:
        subprocess.run([sys.executable, "agent.py"] + failing)
        st.success("Rerun submitted; refresh to see new rows.")
