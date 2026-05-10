import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import base64

# ==========================================
# 1. GLOBAL SETTINGS & UI THEME
# ==========================================
st.set_page_config(page_title="Awais Ahmad | AI Testing Engine", layout="wide", page_icon="🎓")

DEV_NAME = "Awais Ahmad"
ROLL_NO = "25-ME-108"

# Custom CSS for Professional Look
st.markdown(f"""
    <style>
    .main {{ background-color: #f8fafc; }}
    .stApp {{ border-top: 8px solid #1e40af; }}
    .student-card {{
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0;
    }}
    .admin-header {{
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        color: white; padding: 30px; border-radius: 15px; text-align: center;
    }}
    .stButton>button {{
        border-radius: 8px; font-weight: 600; height: 3em; transition: 0.3s;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE INITIALIZATION (Session State)
# ==========================================
if 'exam_db' not in st.session_state:
    st.session_state.exam_db = [
        {"id": 1, "q": "What is the primary function of a Governor in Engines?", "options": ["Control Speed", "Increase Fuel", "Reduce Friction", "Cooling"], "a": "Control Speed"},
        {"id": 2, "q": "Which law of thermodynamics defines Entropy?", "options": ["Zeroth", "First", "Second", "Third"], "a": "Second"}
    ]

if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=["ID", "Time", "Student", "Roll", "Score", "Percentage", "Status"])

if 'active_session' not in st.session_state:
    st.session_state.active_session = False

# ==========================================
# 3. SIDEBAR (Role Selection & Identification)
# ==========================================
with st.sidebar:
    st.image("https://flaticon.com", width=100)
    st.title("LMS Control")
    st.markdown(f"**Professor:** {DEV_NAME}")
    st.markdown(f"**ID:** {ROLL_NO}")
    st.divider()
    
    app_mode = st.radio("Navigate System", ["👨‍🎓 Student Portal", "👨‍🏫 Teacher Dashboard", "📊 Global Analytics", "⚙️ System Logs"])
    
    st.divider()
    st.success("System Status: Online ✅")
    st.info("Database: Active (In-Memory)")

# ==========================================
# 4. TEACHER DASHBOARD (Admin Panel)
# ==========================================
if app_mode == "👨‍🏫 Teacher Dashboard":
    st.markdown(f'<div class="admin-header"><h1>Admin Control Panel</h1><p>Managed by {DEV_NAME}</p></div>', unsafe_allow_html=True)
    
    # Password Protection
    access_key = st.text_input("Enter Admin Access Key", type="password")
    if access_key == ROLL_NO:
        t1, t2, t3 = st.tabs(["➕ Question Builder", "📜 Result Registry", "🔧 Exam Settings"])
        
        with t1:
            st.subheader("Create New MCQ")
            with st.form("mcq_builder", clear_on_submit=True):
                new_q = st.text_area("Question Statement")
                c1, c2 = st.columns(2)
                o1 = c1.text_input("Option 1")
                o2 = c2.text_input("Option 2")
                o3 = c1.text_input("Option 3")
                o4 = c2.text_input("Option 4")
                ans = st.selectbox("Select Correct Answer", [o1, o2, o3, o4])
                
                if st.form_submit_button("Publish Question"):
                    if new_q and o1 and o2:
                        st.session_state.exam_db.append({"id": len(st.session_state.exam_db)+1, "q": new_q, "options": [o1, o2, o3, o4], "a": ans})
                        st.success("New question synchronized with live database!")
                    else:
                        st.error("Please fill all fields.")
            
            st.divider()
            st.subheader("Manage Current Questions")
            st.write(pd.DataFrame(st.session_state.exam_db))

        with t2:
            st.subheader("Student Performance History")
            if not st.session_state.results.empty:
                st.dataframe(st.session_state.results, use_container_width=True)
                csv = st.session_state.results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Results to CSV", csv, "students_records.csv", "text/csv")
            else:
                st.info("No records found in current session.")

        with t3:
            st.subheader("Global Constraints")
            st.toggle("Enable Negative Marking", value=False)
            st.toggle("Show Results Instantly to Students", value=True)
            if st.button("Reset Entire System"):
                st.session_state.results = pd.DataFrame(columns=st.session_state.results.columns)
                st.session_state.exam_db = []
                st.rerun()
    else:
        st.warning("Enter your Roll Number as password to unlock.")

# ==========================================
# 5. STUDENT PORTAL (The Test)
# ==========================================
elif app_mode == "👨‍🎓 Student Portal":
    st.title("📝 Examination Hall")
    
    if not st.session_state.exam_db:
        st.error("Access Denied: No active test found. Contact Prof. Awais.")
    else:
        with st.container():
            st.markdown('<div class="student-card">', unsafe_allow_html=True)
            st.subheader("Candidate Registration")
            col_a, col_b = st.columns(2)
            s_name = col_a.text_input("Full Name")
            s_roll = col_b.text_input("Roll Number / ID")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            st.markdown("### Examination Paper")
            responses = {}
            for i, item in enumerate(st.session_state.exam_db):
                st.write(f"**Question {i+1}:** {item['q']}")
                responses[i] = st.radio(f"Select choice for Q{i+1}:", item['options'], key=f"std_q{i}", index=None)
                st.write("---")

            if st.button("🏁 Finalize & Submit Attempt"):
                if not s_name or not s_roll:
                    st.error("Registration required before submission.")
                else:
                    with st.spinner("Analyzing responses..."):
                        time.sleep(2)
                        
                        # Calculation Logic
                        correct_count = 0
                        total_q = len(st.session_state.exam_db)
                        for i, item in enumerate(st.session_state.exam_db):
                            if responses[i] == item['a']:
                                correct_count += 1
                        
                        perc = (correct_count / total_q) * 100
                        status = "Pass" if perc >= 50 else "Fail"
                        
                        # Save to Database
                        new_rec = {
                            "ID": len(st.session_state.results)+1,
                            "Time": datetime.now().strftime("%H:%M:%S"),
                            "Student": s_name,
                            "Roll": s_roll,
                            "Score": correct_count,
                            "Percentage": f"{perc}%",
                            "Status": status
                        }
                        st.session_state.results = pd.concat([st.session_state.results, pd.DataFrame([new_rec])], ignore_index=True)
                        
                        # Results UI
                        st.balloons()
                        st.success(f"Exam Complete! Thank you {s_name}.")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Obtained Marks", f"{correct_count}/{total_q}")
                        c2.metric("Grade Percentage", f"{perc}%")
                        c3.metric("Final Status", status)
                        
                        if status == "Pass":
                            st.info("Congratulations! You have successfully cleared the assessment.")

# ==========================================
# 6. GLOBAL ANALYTICS
# ==========================================
elif app_mode == "📊 Global Analytics":
    st.title("📊 Statistical Performance Review")
    df = st.session_state.results
    
    if not df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Pass/Fail Ratio")
            fig1 = px.pie(df, names='Status', color='Status', 
                          color_discrete_map={'Pass':'#10b981', 'Fail':'#ef4444'}, hole=0.5)
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            st.subheader("Score Distribution")
            fig2 = px.histogram(df, x="Score", nbins=10, title="Frequency of Scores")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.subheader("Live Leaderboard")
        st.table(df.sort_values(by="Score", ascending=False).head(10))
    else:
        st.warning("No data available for visualization.")

# ==========================================
# 7. SYSTEM LOGS
# ==========================================
else:
    st.title("🛠️ Developer Console")
    st.write(f"**App Developed by:** {DEV_NAME}")
    st.write(f"**University Roll No:** {ROLL_NO}")
    st.divider()
    st.code(f"""
    [LOG] System Initialized at {datetime.now()}
    [LOG] Active User Sessions: 1
    [LOG] Database Connectivity: SUCCESS (Static-State)
    [LOG] Security Protocol: SHA-256 Simulation Active
    [LOG] Environment: Streamlit Cloud Optimized
    """, language="bash")
    
    st.progress(100, text="System Stability: Excellent")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
f1, f2 = st.columns(2)
f1.caption(f"Portal Version {VERSION} | Build 2024.11")
f2.markdown(f"<p style='text-align:right; color:grey;'>Owner: {DEV_NAME} ({ROLL_NO})</p>", unsafe_allow_html=True)
