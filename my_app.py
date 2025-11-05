import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import json
import os
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# CONFIG
# -----------------------------
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]

# -----------------------------
# USER AUTHENTICATION
# -----------------------------
USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    users = load_users()
    if username in users:
        return users[username] == hash_password(password)
    return False

def register_user(username, password, email):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    users[username] = hash_password(password)
    save_users(users)
    return True, "Registration successful"

def login_page():
    st.title("🎓 Student Risk Monitoring System")
    st.markdown("### Welcome Professors! Please login to access the dashboard.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if login_username and login_password:
                if verify_login(login_username, login_password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_username
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.subheader("Sign Up")
        signup_username = st.text_input("Username", key="signup_username")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
        if st.button("Sign Up", type="primary"):
            if signup_username and signup_email and signup_password and signup_password_confirm:
                if signup_password != signup_password_confirm:
                    st.error("Passwords do not match")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register_user(signup_username, signup_password, signup_email)
                    if success:
                        st.success(message)
                        st.info("Go to Login tab to access dashboard")
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('HSU_Student_Success_Data.csv')
    return df

# -----------------------------
# OVERVIEW PAGE
# -----------------------------
def display_overview(df):
    st.subheader("📊 Overview Metrics")
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Students", f"{latest_df['student_id'].nunique():,}")
    col2.metric("At-Risk Students", f"{latest_df['at_risk_flag'].sum():,}", 
                delta=f"{latest_df['at_risk_flag'].mean()*100:.1f}%", delta_color="inverse")
    col3.metric("Low Attendance (<80%)", f"{(latest_df['attendance_rate']<80).sum():,}")
    col4.metric("Low GPA (<2.0)", f"{(latest_df['cum_gpa']<2.0).sum():,}")
    col5.metric("On Probation", f"{latest_df['probation_flag'].sum():,}")

# -----------------------------
# AT-RISK STUDENTS
# -----------------------------
def generate_recommendation(student):
    recs = []
    if student['cum_gpa'] < 2.5:
        recs.append("Schedule tutoring for core courses")
    if student['attendance_rate'] < 80:
        recs.append("Send attendance warning")
    if student['assignments_on_time_pct'] < 75:
        recs.append("Assign mentor for assignment completion")
    if student['course_drop_count'] > 0:
        recs.append("Advise on course selection strategy")
    if student['probation_flag'] == 1:
        recs.append("Discuss probation status with advisor")
    return recs

def send_email(receiver_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def display_at_risk(df):
    st.subheader("🚨 At-Risk Students")
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    if st.checkbox("Show Alert: Dropout Probability > 40%"):
        alert_df = latest_df[latest_df['dropout_probability'] > 0.4]
        st.warning(f"Found {len(alert_df)} students with high dropout probability")
        
        for idx, student in alert_df.iterrows():
            col1, col2 = st.columns([2,3])
            with col1:
                st.write(f"**ID:** {student['student_id']} | **Major:** {student['major']} | GPA: {student['cum_gpa']:.2f} | Attendance: {student['attendance_rate']:.1f}% | Dropout: {student['dropout_probability']*100:.1f}%")
            with col2:
                recs = generate_recommendation(student)
                if recs:
                    st.markdown("**Recommendations:**")
                    for r in recs:
                        st.write(f"- {r}")
                # Email button
                receiver_email = st.text_input(f"Enter recipient email for {student['student_id']}", key=f"email_{student['student_id']}")
                if st.button(f"Send Email to {student['student_id']}", key=f"send_{student['student_id']}"):
                    if receiver_email:
                        body = f"Student ID: {student['student_id']}\nMajor: {student['major']}\nRecommendations:\n" + "\n".join(recs)
                        if send_email(receiver_email, "Student Recommendations", body):
                            st.success(f"Email sent to {receiver_email}")
                    else:
                        st.warning("Please enter an email address")

# -----------------------------
# MANUAL PREDICTION PAGE
# -----------------------------
# -----------------------------
# MANUAL PREDICTION PAGE
# -----------------------------
def display_manual_prediction(df):
    st.subheader("📝 Manual Prediction / Add Student Record")

    with st.form("manual_prediction_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            term = st.number_input("Term", 1, 12, 1)
            cum_gpa = st.number_input("Cumulative GPA", 0.0, 4.0, 3.0, step=0.01)
            attendance_rate = st.number_input("Attendance Rate (%)", 0, 100, 90)
        with col2:
            assignments_on_time_pct = st.number_input("Assignments On Time (%)", 0, 100, 90)
            course_drop_count = st.number_input("Course Drop Count", 0, 10, 0)
            probation_flag = st.selectbox("On Probation?", [0, 1])
        with col3:
            lms_logins = st.number_input("LMS Logins", 0, 1000, 10)
            advisor_meetings = st.number_input("Advisor Meetings", 0, 50, 1)
            tutoring_sessions = st.number_input("Tutoring Sessions", 0, 50, 0)

        # ✅ Correct button for forms
        submitted = st.form_submit_button("Predict Dropout Risk")

        if submitted:
            risk_score = 0
            if cum_gpa < 2.5: risk_score += 30
            elif cum_gpa < 3.0: risk_score += 15
            if attendance_rate < 80: risk_score += 25
            elif attendance_rate < 90: risk_score += 10
            if assignments_on_time_pct < 75: risk_score += 15
            if course_drop_count > 0: risk_score += 10
            if probation_flag == 1: risk_score += 20

            probability = min(risk_score, 100) / 100
            risk_flag = 1 if probability >= 0.4 else 0

            st.markdown(f"**Predicted Dropout Probability:** {probability*100:.1f}%")
            st.markdown(f"**Risk Status:** {'🚨 AT RISK' if risk_flag==1 else '✅ Not At Risk'}")

            recs = generate_recommendation({
                'cum_gpa': cum_gpa,
                'attendance_rate': attendance_rate,
                'assignments_on_time_pct': assignments_on_time_pct,
                'course_drop_count': course_drop_count,
                'probation_flag': probation_flag,
                'major': 'N/A',
                'student_id': 'Manual Entry'
            })

            # ✅ Moved email field and button OUTSIDE the form
    st.markdown("---")
    st.subheader("📩 Send Recommendation Email (Optional)")
    receiver_email = st.text_input("Enter recipient email for manual prediction", key="manual_email")
    if st.button("Send Recommendation Email", key="manual_send"):
        if receiver_email:
            body = f"Predicted Dropout Probability: {probability*100:.1f}%\nRisk Status: {'AT RISK' if risk_flag==1 else 'Not At Risk'}\nRecommendations:\n" + "\n".join(recs)
            if send_email(receiver_email, "Student Recommendations", body):
                st.success(f"Email sent to {receiver_email}")
        else:
            st.warning("Please enter an email address")

# -----------------------------
# MAIN APP
# -----------------------------
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_page()
    else:
        with st.sidebar:
            st.title("🎓 Dashboard Navigation")
            st.write(f"**Logged in as:** {st.session_state['username']}")
            page = st.radio("Select Page", ["Overview","At-Risk Students","Analytics","Student Search","Manual Prediction"])
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.experimental_rerun()

        df = load_data()
        st.title("📊 Student Risk Monitoring Dashboard")
        st.markdown(f"*Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        st.markdown("---")

        if page=="Overview":
            display_overview(df)
        elif page=="At-Risk Students":
            display_at_risk(df)
        elif page=="Analytics":
            display_analytics(df)
        elif page=="Student Search":
            display_student_search(df)
        elif page=="Manual Prediction":
            display_manual_prediction(df)

# -----------------------------
# Analytics and Search Pages (unchanged)
# -----------------------------
def display_analytics(df):
    st.subheader("📈 Analytics")
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.histogram(latest_df, x='attendance_rate', nbins=20, title="Attendance Distribution", color_discrete_sequence=['#1f77b4'])
        fig1.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="80% Threshold")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.histogram(latest_df, x='cum_gpa', nbins=20, title="Cumulative GPA Distribution", color_discrete_sequence=['#2ca02c'])
        fig2.add_vline(x=2.0, line_dash="dash", line_color="red", annotation_text="2.0 Threshold")
        st.plotly_chart(fig2, use_container_width=True)

def display_student_search(df):
    st.subheader("🔍 Student Search")
    search_id = st.text_input("Enter Student ID")
    if search_id:
        student_data = df[df['student_id']==search_id]
        if not student_data.empty:
            latest_record = student_data.sort_values('term').iloc[-1]
            st.metric("Major", latest_record['major'])
            st.metric("Cumulative GPA", f"{latest_record['cum_gpa']:.2f}")
            st.metric("Attendance", f"{latest_record['attendance_rate']:.1f}%")
            risk_status = "🚨 AT RISK" if latest_record['at_risk_flag']==1 else "✅ Not At Risk"
            st.metric("Risk Status", risk_status)
            
            st.markdown("#### Term-by-Term GPA Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=student_data['term'], y=student_data['gpa_term'], mode='lines+markers', name='Term GPA'))
            fig.add_trace(go.Scatter(x=student_data['term'], y=student_data['cum_gpa'], mode='lines+markers', name='Cumulative GPA'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No record found")

if __name__=="__main__":
    main()
