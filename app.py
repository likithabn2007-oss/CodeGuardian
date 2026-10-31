import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import re
import json
import os

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="EquiCode Scanner", page_icon="🔍", layout="wide")

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = "equicode_db"

@st.cache_resource
def get_db_engine():
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

engine = get_db_engine()

# ==========================================
# 2. STATIC CODE ANALYSIS ENGINE (NO AI)
# ==========================================
def analyze_code_statically(code: str):
    """Rule-based engine that scans for specific patterns without using AI."""
    feedback = []
    sec_score = 100
    inc_score = 100
    acc_score = 100
    refactored_code = code

    # Security Rules
    if re.search(r'(password|secret|api_key)\s*=\s*[\'"].+[\'"]', code, re.I):
        sec_score -= 40
        feedback.append("CRITICAL: Hardcoded secrets or passwords detected. Use environment variables.")
    
    if "SELECT * FROM" in code.upper():
        sec_score -= 20
        feedback.append("SECURITY: Avoid 'SELECT *'. It can expose sensitive data and degrade performance.")

    # Inclusivity Rules
    non_inclusive = {'master': 'primary', 'slave': 'replica', 'whitelist': 'allowlist', 'blacklist': 'denylist'}
    for bad_word, good_word in non_inclusive.items():
        if re.search(r'\b' + bad_word + r'\b', code, re.IGNORECASE):
            inc_score -= 25
            feedback.append(f"INCLUSIVITY: Found non-inclusive term '{bad_word}'. Recommended replacement: '{good_word}'.")
            # Auto-replace for the refactored output
            refactored_code = re.sub(r'\b' + bad_word + r'\b', good_word, refactored_code, flags=re.IGNORECASE)

    # Accessibility Rules (Basic HTML check)
    if "<img" in code and "alt=" not in code:
        acc_score -= 30
        feedback.append("ACCESSIBILITY: Image tags found without 'alt' attributes. Screen readers require alt text.")

    if not feedback:
        feedback.append("Code passed all static analysis checks. No issues found.")

    return {
        "security_score": max(0, sec_score),
        "accessibility_score": max(0, acc_score),
        "inclusivity_score": max(0, inc_score),
        "feedback_points": feedback,
        "refactored_code": refactored_code
    }

def save_to_mysql(team, pr_title, result):
    query = text("""
        INSERT INTO pr_reviews 
        (team_name, pr_title, security_score, accessibility_score, inclusivity_score, ai_analysis, refactored_code) 
        VALUES (:team, :pr, :sec, :acc, :inc, :analysis, :code)
    """)
    with engine.connect() as conn:
        conn.execute(query, {
            "team": team, "pr": pr_title,
            "sec": result["security_score"], "acc": result["accessibility_score"], "inc": result["inclusivity_score"],
            "analysis": json.dumps(result["feedback_points"]), "code": result["refactored_code"]
        })
        conn.commit()

# ==========================================
# 3. FRONTEND UI
# ==========================================
st.title("🔍 EquiCode Scanner: Static PR Auditor")
st.markdown("Fast, rule-based static analysis for security and inclusivity.")

tab1, tab2 = st.tabs(["Scan Pull Request", "Dashboard"])

with tab1:
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            team_name = st.text_input("Engineering Squad", placeholder="e.g., Backend Team")
            pr_title = st.text_input("Pull Request Title", placeholder="e.g., Update database schema")
        with col2:
            code_input = st.text_area("Paste Code Here", height=150)
            
        if st.button("Run Static Scan", type="primary", use_container_width=True):
            if code_input and team_name:
                with st.spinner("Running regex patterns and static checks..."):
                    result = analyze_code_statically(code_input)
                    save_to_mysql(team_name, pr_title, result)
                    st.toast("Scan saved to MySQL database!", icon="✅")
                    
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Security Score", f"{result['security_score']}/100")
                    s2.metric("Accessibility Score", f"{result['accessibility_score']}/100")
                    s3.metric("Inclusivity Score", f"{result['inclusivity_score']}/100")
                    
                    st.subheader("Scanner Feedback")
                    for point in result["feedback_points"]:
                        st.markdown(f"- {point}")
                        
                    with st.expander("View Auto-Corrected Code", expanded=True):
                        st.code(result["refactored_code"], language="python")
            else:
                st.warning("Please provide Team Name and Code to review.")

with tab2:
    st.subheader("Organization-Wide Health Metrics")
    try:
        df = pd.read_sql("SELECT * FROM pr_reviews ORDER BY reviewed_at DESC", con=engine)
        if not df.empty:
            avg_sec = df['security_score'].mean()
            avg_acc = df['accessibility_score'].mean()
            avg_inc = df['inclusivity_score'].mean()
            
            fig = go.Figure(data=go.Scatterpolar(
              r=[avg_sec, avg_acc, avg_inc],
              theta=['Security', 'Accessibility', 'Inclusivity'],
              fill='toself'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Global Averages")
            
            col_chart, col_data = st.columns([1, 2])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_data:
                st.dataframe(df[['reviewed_at', 'team_name', 'pr_title', 'security_score', 'inclusivity_score']], use_container_width=True)
        else:
            st.info("No PRs scanned yet.")
    except Exception as e:
        st.error(f"Database error: {e}")
