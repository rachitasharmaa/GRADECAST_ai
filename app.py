import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
API_URL = "https://gradecast.onrender.com/prediction"

USERS = {
    "student@test.com": {"password": "student123", "role": "Student", "name": "Alex Student"},
    "9876543210":       {"password": "student123", "role": "Student", "name": "Alex Student"},
    "teacher@test.com": {"password": "teacher123", "role": "Teacher", "name": "Dr. Smith"},
    "9000000001":       {"password": "teacher123", "role": "Teacher", "name": "Dr. Smith"},
}

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GradeCast AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .grade-badge {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        padding: 1rem 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        margin: 1rem auto;
        display: inline-block;
    }
    .feedback-box {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        background: #F0FDF4;
        border-left: 4px solid #22C55E;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        background: #FFF7ED;
        border-left: 4px solid #F97316;
        margin: 1rem 0;
    }
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem;
    }
    .metric-container {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "role": None,
        "history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ─────────────────────────────────────────────
# AUTH FUNCTIONS
# ─────────────────────────────────────────────
def authenticate(identifier, password):
    user = USERS.get(identifier.strip())
    if user and user["password"] == password:
        return user
    return None

def logout():
    for key in ["logged_in", "user", "role", "history"]:
        st.session_state[key] = None if key == "user" else (False if key == "logged_in" else [])

# ─────────────────────────────────────────────
# API CALL
# ─────────────────────────────────────────────
def get_prediction(marks, study_hours, attendance, previous_gpa):
    payload = {
        "marks": marks,
        "study_hours": study_hours,
        "attendance": attendance,
        "previous_gpa": previous_gpa
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("predicted_grade") or data.get("grade") or data.get("prediction"), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot reach prediction server. Check your internet connection."
    except requests.exceptions.Timeout:
        return None, "⏱️ Server took too long to respond. Try again in a moment."
    except requests.exceptions.HTTPError as e:
        return None, f"🚫 Server error: {e}"
    except Exception as e:
        return None, f"⚠️ Unexpected error: {e}"

# ─────────────────────────────────────────────
# SMART FEEDBACK
# ─────────────────────────────────────────────
def generate_feedback(marks, study_hours, attendance, previous_gpa, grade):
    feedback = []
    warnings = []

    if marks < 50:
        warnings.append("📉 Your marks are below 50. Focus on core concepts and practice more problems.")
    elif marks < 70:
        feedback.append("📘 Marks are decent. Push past 70 for stronger grade outcomes.")
    else:
        feedback.append("✅ Great marks! Keep maintaining this level.")

    if study_hours < 2:
        warnings.append("⏰ Only studying under 2 hours/day. Try to increase to at least 3–4 hours.")
    elif study_hours >= 4:
        feedback.append("🏆 Excellent study hours! Consistency here drives results.")

    if attendance < 75:
        warnings.append("🚨 Attendance below 75% — this directly hurts exam eligibility in most colleges.")
    elif attendance >= 90:
        feedback.append("🎯 Perfect attendance! You're capturing all class content.")

    if previous_gpa < 5.0:
        warnings.append("📊 Previous GPA is low. Create a structured study plan immediately.")
    elif previous_gpa >= 8.0:
        feedback.append("🌟 Strong previous GPA shows consistent performance.")

    return feedback, warnings

# ─────────────────────────────────────────────
# INPUT FORM (shared by student & teacher)
# ─────────────────────────────────────────────
def prediction_form(prefix=""):
    col1, col2 = st.columns(2)
    with col1:
        marks = st.slider(f"{prefix}📊 Marks (out of 100)", 0, 100, 65, key=f"{prefix}_marks")
        study_hours = st.slider(f"{prefix}📚 Daily Study Hours", 0, 12, 4, key=f"{prefix}_study")
    with col2:
        attendance = st.slider(f"{prefix}📅 Attendance (%)", 0, 100, 80, key=f"{prefix}_attend")
        previous_gpa = st.slider(f"{prefix}🎓 Previous GPA (out of 10)", 0.0, 10.0, 7.0,
                                  step=0.1, key=f"{prefix}_gpa")

    return marks, study_hours, attendance, previous_gpa

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def login_page():
    st.markdown('<div class="main-header">🎓 GradeCast AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered academic performance predictor</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login to your account")

        with st.container():
            identifier = st.text_input("📧 Email or 📱 Phone Number",
                                        placeholder="e.g. student@test.com or 9876543210")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

            if st.button("Login →", type="primary"):
                if not identifier or not password:
                    st.error("⚠️ Please fill in both fields.")
                else:
                    user = authenticate(identifier, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user["role"]
                        st.session_state.history = []
                        st.success(f"✅ Welcome, {user['name']}! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")

        st.divider()
        st.markdown("**Demo Accounts:**")
        st.markdown("🎓 Student: `student@test.com` / `student123`")
        st.markdown("👨‍🏫 Teacher: `teacher@test.com` / `teacher123`")

# ─────────────────────────────────────────────
# STUDENT DASHBOARD
# ─────────────────────────────────────────────
def student_dashboard():
    user = st.session_state.user

    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.markdown(f"Role: **{st.session_state.role}**")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.markdown(f"## 🎓 Student Dashboard — Welcome, {user['name']}!")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📊 Predict Grade", "📜 History", "📈 Analytics"])

    # ── TAB 1: PREDICT ──
    with tab1:
        st.markdown("### Enter Your Academic Details")
        marks, study_hours, attendance, previous_gpa = prediction_form("stu")

        if st.button("🚀 Predict My Grade", type="primary"):
            with st.spinner("Contacting AI prediction server..."):
                grade, error = get_prediction(marks, study_hours, attendance, previous_gpa)

            if error:
                st.error(error)
            elif grade:
                st.balloons()
                st.markdown("---")
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.markdown("### 🏆 Predicted Grade")
                    st.markdown(f'<div class="grade-badge">{grade}</div>', unsafe_allow_html=True)

                with col_b:
                    feedback, warnings = generate_feedback(
                        marks, study_hours, attendance, previous_gpa, grade)

                    if feedback:
                        st.markdown("**✅ Strengths:**")
                        for f in feedback:
                            st.markdown(f'<div class="feedback-box">{f}</div>',
                                        unsafe_allow_html=True)
                    if warnings:
                        st.markdown("**⚠️ Areas to improve:**")
                        for w in warnings:
                            st.markdown(f'<div class="warning-box">{w}</div>',
                                        unsafe_allow_html=True)

                # Save to history
                st.session_state.history.append({
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Marks": marks,
                    "Study Hrs": study_hours,
                    "Attendance": attendance,
                    "GPA": previous_gpa,
                    "Predicted Grade": grade
                })
            else:
                st.warning("⚠️ No grade returned from server. Check your API.")

    # ── TAB 2: HISTORY ──
    with tab2:
        st.markdown("### 📜 Your Prediction History")
        if not st.session_state.history:
            st.info("No predictions yet. Go to 'Predict Grade' to get started!")
        else:
            df = pd.DataFrame(st.session_state.history)
            st.dataframe(df, use_container_width=True)
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.rerun()

    # ── TAB 3: ANALYTICS ──
    with tab3:
        st.markdown("### 📈 Performance Analytics")
        if len(st.session_state.history) < 2:
            st.info("Make at least 2 predictions to see analytics.")
        else:
            df = pd.DataFrame(st.session_state.history)
            fig = px.line(df, x="Time", y="Marks",
                          title="Marks Over Predictions",
                          markers=True, color_discrete_sequence=["#4F46E5"])
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.bar(df, x="Time", y="Study Hrs",
                          title="Study Hours Per Session",
                          color_discrete_sequence=["#7C3AED"])
            st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# TEACHER DASHBOARD
# ─────────────────────────────────────────────
def teacher_dashboard():
    user = st.session_state.user

    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.markdown(f"Role: **{st.session_state.role}**")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.markdown(f"## 👨‍🏫 Teacher Dashboard — Welcome, {user['name']}!")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🔮 Predict (Self)", "👥 Compare Students", "📊 Batch Analytics"])

    # ── TAB 1: SELF PREDICT ──
    with tab1:
        st.markdown("### 🔮 Self Prediction (same as student view)")
        marks, study_hours, attendance, previous_gpa = prediction_form("tea")

        if st.button("🚀 Predict Grade", type="primary"):
            with st.spinner("Predicting..."):
                grade, error = get_prediction(marks, study_hours, attendance, previous_gpa)
            if error:
                st.error(error)
            elif grade:
                st.success(f"✅ Predicted Grade: **{grade}**")
                feedback, warnings = generate_feedback(
                    marks, study_hours, attendance, previous_gpa, grade)
                for f in feedback:
                    st.markdown(f'<div class="feedback-box">{f}</div>', unsafe_allow_html=True)
                for w in warnings:
                    st.markdown(f'<div class="warning-box">{w}</div>', unsafe_allow_html=True)

    # ── TAB 2: COMPARE ──
    with tab2:
        st.markdown("### 👥 Compare Multiple Students")
        num_students = st.slider("How many students to compare?", 2, 5, 3)

        student_data = []
        for i in range(num_students):
            st.markdown(f"#### Student {i+1}")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                name = st.text_input("Name", value=f"Student {i+1}", key=f"name_{i}")
            with c2:
                m = st.number_input("Marks", 0, 100, 65, key=f"m_{i}")
            with c3:
                s = st.number_input("Study Hrs", 0, 12, 4, key=f"s_{i}")
            with c4:
                a = st.number_input("Attendance%", 0, 100, 80, key=f"a_{i}")
            with c5:
                g = st.number_input("GPA", 0.0, 10.0, 7.0, step=0.1, key=f"g_{i}")
            student_data.append({"name": name, "marks": m,
                                  "study": s, "attend": a, "gpa": g})

        if st.button("📊 Compare All Students", type="primary"):
            results = []
            progress = st.progress(0)
            for idx, s in enumerate(student_data):
                grade, err = get_prediction(s["marks"], s["study"], s["attend"], s["gpa"])
                results.append({
                    "Student": s["name"],
                    "Marks": s["marks"],
                    "Study Hrs": s["study"],
                    "Attendance": s["attend"],
                    "GPA": s["gpa"],
                    "Predicted Grade": grade or "Error"
                })
                progress.progress((idx + 1) / len(student_data))

            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            fig = go.Figure()
            metrics = ["Marks", "Study Hrs", "Attendance", "GPA"]
            colors = ["#4F46E5", "#7C3AED", "#EC4899", "#F97316", "#22C55E"]
            for i, row in df.iterrows():
                fig.add_trace(go.Bar(
                    name=row["Student"],
                    x=metrics,
                    y=[row["Marks"], row["Study Hrs"] * 8,
                       row["Attendance"], row["GPA"] * 10],
                    marker_color=colors[i % len(colors)]
                ))
            fig.update_layout(barmode="group", title="Student Performance Comparison",
                              yaxis_title="Score (normalized to 100)")
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 3: BATCH ANALYTICS ──
    with tab3:
        st.markdown("### 📊 Quick Batch Analysis")
        st.info("Use the 'Compare Students' tab first, then come back here for insights.")

        sample_data = {
            "Student": ["Alice", "Bob", "Carol", "David", "Eve"],
            "Marks":   [88, 62, 74, 91, 55],
            "Study Hrs": [6, 3, 4, 7, 2],
            "Attendance": [95, 70, 82, 98, 65]
        }
        df_sample = pd.DataFrame(sample_data)
        st.markdown("**Sample Class Overview:**")
        fig = px.scatter(df_sample, x="Study Hrs", y="Marks",
                         size="Attendance", color="Student",
                         title="Study Hours vs Marks (bubble = attendance)")
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────
def main():
    init_session()

    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.role == "Student":
        student_dashboard()
    elif st.session_state.role == "Teacher":
        teacher_dashboard()
    else:
        st.error("Unknown role. Please logout and try again.")
        if st.button("Logout"):
            logout()
            st.rerun()

if __name__ == "__main__":
    main()