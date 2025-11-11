import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import json
import os
import joblib
from sklearn.preprocessing import StandardScaler

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

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('hsu_complete_dataset_with_predictions.csv')
    return df

# -----------------------------
# EMAIL FUNCTION
# -----------------------------
def send_email(receiver_email, subject, body):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

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

# -----------------------------
# RECOMMENDATION GENERATOR
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

# -----------------------------
# OVERVIEW PAGE
# -----------------------------
def display_overview(df):
    st.subheader("📊 Overview Metrics")
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Students", f"{latest_df['student_id'].nunique():,}")
    col2.metric("At-Risk Students", f"{latest_df['pred_at_risk_flag'].sum():,}", 
                delta=f"{latest_df['pred_at_risk_flag'].mean()*100:.1f}%", delta_color="inverse")
    col3.metric("Low Attendance (<80%)", f"{(latest_df['attendance_rate']<80).sum():,}")
    col4.metric("Low GPA (<2.0)", f"{(latest_df['cum_gpa']<2.0).sum():,}")
    col5.metric("On Probation", f"{latest_df['probation_flag'].sum():,}")

# -----------------------------
# AT-RISK STUDENTS PAGE
# -----------------------------
def display_at_risk(df):
    st.subheader("🚨 At-Risk Students")
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    alert_df = latest_df[latest_df['pred_dropout_probability'] > 0.4]

    st.warning(f"Found {len(alert_df)} students with high predicted dropout probability")

    for idx, student in alert_df.iterrows():
        col1, col2 = st.columns([2,3])
        with col1:
            st.write(f"**ID:** {student['student_id']} | **Major:** {student['major']} | GPA: {student['cum_gpa']:.2f} | Attendance: {student['attendance_rate']:.1f}% | Dropout: {student['pred_dropout_probability']*100:.1f}%")
        with col2:
            recs = generate_recommendation(student)
            if recs:
                st.markdown("**Recommendations:**")
                for r in recs:
                    st.write(f"- {r}")

            # Email input and send button
            receiver_email = st.text_input(f"Enter email for {student['student_id']}", key=f"email_{student['student_id']}")
            if st.button(f"Send Email to {student['student_id']}", key=f"send_{student['student_id']}"):
                if receiver_email:
                    body = f"Student ID: {student['student_id']}\nMajor: {student['major']}\nGPA: {student['cum_gpa']:.2f}\nAttendance: {student['attendance_rate']:.1f}%\nPredicted Dropout Risk: {student['pred_dropout_probability']*100:.1f}%\n\nRecommendations:\n" + "\n".join(recs)
                    if send_email(receiver_email, "Student Recommendations", body):
                        st.success(f"Email sent to {receiver_email}")
                else:
                    st.warning("Please enter an email address")

# -----------------------------
# AT-RISK STUDENTS DATA PAGE
# -----------------------------
def display_at_risk_students_data(df):
    st.subheader("📋 At-Risk Students Data")
    at_risk_df = df[df['pred_at_risk_flag'] == 1].copy()
    at_risk_df = at_risk_df.sort_values('term').groupby('student_id').last().reset_index()

    col1, col2, col3 = st.columns(3)
    with col1:
        major_filter = st.multiselect("Filter by Major", options=sorted(at_risk_df['major'].unique()), default=None)
    with col2:
        gpa_filter = st.slider("Maximum GPA", 0.0, 4.0, 4.0, 0.1)
    with col3:
        attendance_filter = st.slider("Maximum Attendance %", 0, 100, 100, 5)

    filtered_df = at_risk_df.copy()
    if major_filter:
        filtered_df = filtered_df[filtered_df['major'].isin(major_filter)]
    filtered_df = filtered_df[filtered_df['cum_gpa'] <= gpa_filter]
    filtered_df = filtered_df[filtered_df['attendance_rate'] <= attendance_filter]

    st.write(f"**Showing {len(filtered_df)} at-risk students**")

    display_columns = [
        'student_id', 'major', 'term', 'cum_gpa', 'attendance_rate', 
        'assignments_on_time_pct', 'course_drop_count', 'probation_flag',
        'pred_dropout_probability'
    ]

    display_df = filtered_df[display_columns].copy()
    display_df['pred_dropout_probability'] = display_df['pred_dropout_probability'].apply(lambda x: f"{x*100:.1f}%")
    display_df['attendance_rate'] = display_df['attendance_rate'].apply(lambda x: f"{x:.1f}%")
    display_df['assignments_on_time_pct'] = display_df['assignments_on_time_pct'].apply(lambda x: f"{x:.1f}%")

    display_df.columns = [
        'Student ID', 'Major', 'Term', 'Cumulative GPA', 'Attendance Rate',
        'Assignments On Time', 'Course Drops', 'On Probation', 'Dropout Risk'
    ]

    st.dataframe(display_df, use_container_width=True, height=400)

    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download At-Risk Students Data",
        data=csv,
        file_name=f"at_risk_students_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# -----------------------------
# ANALYTICS PAGE
# -----------------------------
def display_analytics(df):
    st.subheader("📈 Analytics")
    # Get latest data for each student
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    # 1. Attendance Distribution
    with col1:
        st.markdown("#### Attendance Rate Distribution")
        fig1 = px.histogram(latest_df, x='attendance_rate', 
                           nbins=20,
                           labels={'attendance_rate': 'Attendance Rate (%)', 'count': 'Number of Students'},
                           color_discrete_sequence=['#1f77b4'])
        fig1.add_vline(x=80, line_dash="dash", line_color="red", 
                      annotation_text="80% Threshold")
        st.plotly_chart(fig1, use_container_width=True)
    
    # 2. GPA Distribution
    with col2:
        st.markdown("#### Cumulative GPA Distribution")
        fig2 = px.histogram(latest_df, x='cum_gpa', 
                           nbins=20,
                           labels={'cum_gpa': 'Cumulative GPA', 'count': 'Number of Students'},
                           color_discrete_sequence=['#2ca02c'])
        fig2.add_vline(x=2.0, line_dash="dash", line_color="red", 
                      annotation_text="2.0 Threshold")
        st.plotly_chart(fig2, use_container_width=True)
    
    # 3. At-Risk Students by Major
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### At-Risk Students by Major (Predicted)")
        risk_by_major = latest_df.groupby('major')['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        risk_by_major['percentage'] = (risk_by_major['sum'] / risk_by_major['count'] * 100).round(1)
        risk_by_major = risk_by_major.sort_values('sum', ascending=True).tail(10)
        
        fig3 = px.bar(risk_by_major, x='sum', y='major', 
                     orientation='h',
                     labels={'sum': 'Number of At-Risk Students', 'major': 'Major'},
                     color='percentage',
                     color_continuous_scale='Reds',
                     text='sum')
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)
    
    # 4. Assignment Completion vs GPA
    with col4:
        st.markdown("#### Assignment Completion vs GPA")
        sample_df = latest_df.sample(min(1000, len(latest_df)))
        fig4 = px.scatter(sample_df, x='assignments_on_time_pct', y='cum_gpa',
                         color='pred_at_risk_flag',
                         labels={'assignments_on_time_pct': 'Assignments On Time (%)',
                                'cum_gpa': 'Cumulative GPA',
                                'pred_at_risk_flag': 'Predicted At Risk'},
                         color_discrete_map={0: '#2ca02c', 1: '#d62728'},
                         opacity=0.6)
        st.plotly_chart(fig4, use_container_width=True)
    
    # 5. Key Risk Indicators
    st.markdown("#### Key Risk Indicators")
    col5, col6, col7 = st.columns(3)
    
    with col5:
        # Low Attendance Analysis
        low_attendance_bins = pd.cut(latest_df['attendance_rate'], 
                                    bins=[0, 60, 70, 80, 90, 100],
                                    labels=['<60%', '60-70%', '70-80%', '80-90%', '90-100%'])
        attendance_counts = low_attendance_bins.value_counts().sort_index()
        
        fig5 = px.bar(x=attendance_counts.index, y=attendance_counts.values,
                     labels={'x': 'Attendance Range', 'y': 'Number of Students'},
                     title='Students by Attendance Range',
                     color=attendance_counts.values,
                     color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig5, use_container_width=True)
    
    with col6:
        # Course Drop Analysis
        drop_counts = latest_df['course_drop_count'].value_counts().sort_index()
        fig6 = px.bar(x=drop_counts.index, y=drop_counts.values,
                     labels={'x': 'Number of Course Drops', 'y': 'Number of Students'},
                     title='Students by Course Drops',
                     color=drop_counts.values,
                     color_continuous_scale='Oranges')
        st.plotly_chart(fig6, use_container_width=True)
    
    with col7:
        # Probation Status
        probation_data = latest_df['probation_flag'].value_counts()
        fig7 = px.pie(values=probation_data.values, 
                     names=['Not on Probation', 'On Probation'],
                     title='Probation Status',
                     color_discrete_sequence=['#2ca02c', '#d62728'])
        st.plotly_chart(fig7, use_container_width=True)
    
    # 6. Engagement Metrics
    st.markdown("#### Student Engagement Metrics")
    col8, col9 = st.columns(2)
    
    with col8:
        # LMS Logins vs At-Risk
        fig8 = px.box(latest_df, x='pred_at_risk_flag', y='lms_logins',
                     labels={'pred_at_risk_flag': 'Predicted Risk Status', 'lms_logins': 'LMS Logins'},
                     title='LMS Logins by Predicted Risk Status',
                     color='pred_at_risk_flag',
                     color_discrete_map={0: '#2ca02c', 1: '#d62728'})
        fig8.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0, 1])
        st.plotly_chart(fig8, use_container_width=True)
    
    with col9:
        # Advisor Meetings
        fig9 = px.box(latest_df, x='pred_at_risk_flag', y='advisor_meetings',
                     labels={'pred_at_risk_flag': 'Predicted Risk Status', 'advisor_meetings': 'Advisor Meetings'},
                     title='Advisor Meetings by Predicted Risk Status',
                     color='pred_at_risk_flag',
                     color_discrete_map={0: '#2ca02c', 1: '#d62728'})
        fig9.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0, 1])
        st.plotly_chart(fig9, use_container_width=True)
    
    # 7. Dropout Probability Distribution
    st.markdown("#### Predicted Dropout Probability Analysis")
    col10, col11 = st.columns(2)
    
    with col10:
        fig10 = px.histogram(latest_df, x='pred_dropout_probability',
                            nbins=30,
                            labels={'pred_dropout_probability': 'Predicted Dropout Probability', 'count': 'Number of Students'},
                            title='Distribution of Predicted Dropout Probability',
                            color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig10, use_container_width=True)
    
    with col11:
        # High risk students (dropout probability > 0.5)
        risk_levels = pd.cut(latest_df['pred_dropout_probability'], 
                           bins=[0, 0.25, 0.5, 0.75, 1.0],
                           labels=['Low (0-25%)', 'Medium (25-50%)', 'High (50-75%)', 'Very High (75-100%)'])
        risk_counts = risk_levels.value_counts()
        
        fig11 = px.pie(values=risk_counts.values, names=risk_counts.index,
                      title='Students by Dropout Risk Level',
                      color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig11, use_container_width=True)
    
    # 8. Financial and Work Analysis
    st.markdown("#### Financial Aid & Work Hours Analysis")
    col12, col13 = st.columns(2)
    
    with col12:
        # Financial Aid Status
        financial_risk = latest_df.groupby('financial_aid_flag')['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        financial_risk['percentage'] = (financial_risk['sum'] / financial_risk['count'] * 100).round(1)
        
        fig12 = px.bar(financial_risk, x='financial_aid_flag', y='sum',
                      labels={'financial_aid_flag': 'Financial Aid Status', 'sum': 'At-Risk Students'},
                      title='At-Risk Students by Financial Aid Status',
                      color='percentage',
                      color_continuous_scale='Blues',
                      text='sum')
        fig12.update_xaxes(ticktext=['No Financial Aid', 'Has Financial Aid'], tickvals=[0, 1])
        fig12.update_traces(textposition='outside')
        st.plotly_chart(fig12, use_container_width=True)
    
    with col13:
        # Work Hours Distribution
        work_bins = pd.cut(latest_df['work_hours_per_week'], 
                          bins=[-1, 0, 10, 20, 30, 100],
                          labels=['Not Working', '1-10 hrs', '11-20 hrs', '21-30 hrs', '30+ hrs'])
        work_counts = work_bins.value_counts().sort_index()
        
        fig13 = px.bar(x=work_counts.index, y=work_counts.values,
                      labels={'x': 'Work Hours per Week', 'y': 'Number of Students'},
                      title='Students by Work Hours',
                      color=work_counts.values,
                      color_continuous_scale='Viridis')
        st.plotly_chart(fig13, use_container_width=True)
    
    # 9. Student Demographics Analysis
    st.markdown("#### Demographics & Enrollment Analysis")
    col14, col15, col16 = st.columns(3)
    
    with col14:
        # Gender Distribution
        gender_data = latest_df['gender'].value_counts()
        fig14 = px.pie(values=gender_data.values, names=gender_data.index,
                      title='Students by Gender',
                      color_discrete_sequence=px.colors.sequential.Purples_r)
        st.plotly_chart(fig14, use_container_width=True)
    
    with col15:
        # Enrollment Status
        enrollment_data = latest_df['enrollment_status'].value_counts()
        fig15 = px.pie(values=enrollment_data.values, names=enrollment_data.index,
                      title='Enrollment Status',
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig15, use_container_width=True)
    
    with col16:
        # First Generation Students
        first_gen_data = latest_df['first_generation_flag'].value_counts()
        fig16 = px.pie(values=first_gen_data.values, 
                      names=['Not First Gen', 'First Generation'],
                      title='First Generation Status',
                      color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig16, use_container_width=True)
    
    # 10. Support Services Utilization
    st.markdown("#### Support Services Utilization")
    col17, col18 = st.columns(2)
    
    with col17:
        # Tutoring Sessions
        fig17 = px.box(latest_df, x='pred_at_risk_flag', y='tutoring_sessions',
                      labels={'pred_at_risk_flag': 'Predicted Risk Status', 'tutoring_sessions': 'Tutoring Sessions'},
                      title='Tutoring Sessions by Predicted Risk Status',
                      color='pred_at_risk_flag',
                      color_discrete_map={0: '#2ca02c', 1: '#d62728'})
        fig17.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0, 1])
        st.plotly_chart(fig17, use_container_width=True)
    
    with col18:
        # Library Visits
        fig18 = px.box(latest_df, x='pred_at_risk_flag', y='library_visits',
                      labels={'pred_at_risk_flag': 'Predicted Risk Status', 'library_visits': 'Library Visits'},
                      title='Library Visits by Predicted Risk Status',
                      color='pred_at_risk_flag',
                      color_discrete_map={0: '#2ca02c', 1: '#d62728'})
        fig18.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0, 1])
        st.plotly_chart(fig18, use_container_width=True)
    
    # 11. Discussion Posts & Engagement
    st.markdown("#### Online Engagement Analysis")
    col19, col20 = st.columns(2)
    
    with col19:
        # Discussion Posts Distribution
        fig19 = px.histogram(latest_df, x='discussion_posts',
                           nbins=20,
                           labels={'discussion_posts': 'Discussion Posts', 'count': 'Number of Students'},
                           title='Distribution of Discussion Posts',
                           color_discrete_sequence=['#9467bd'])
        st.plotly_chart(fig19, use_container_width=True)
    
    with col20:
        # Discussion Posts vs At-Risk
        fig20 = px.box(latest_df, x='pred_at_risk_flag', y='discussion_posts',
                      labels={'pred_at_risk_flag': 'Predicted Risk Status', 'discussion_posts': 'Discussion Posts'},
                      title='Discussion Posts by Predicted Risk Status',
                      color='pred_at_risk_flag',
                      color_discrete_map={0: '#2ca02c', 1: '#d62728'})
        fig20.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0, 1])
        st.plotly_chart(fig20, use_container_width=True)
    
    # 12. Credits and Academic Load
    st.markdown("#### Academic Load Analysis")
    col21, col22 = st.columns(2)
    
    with col21:
        # Credits Attempted Distribution
        fig21 = px.histogram(latest_df, x='credits_attempted',
                           nbins=15,
                           labels={'credits_attempted': 'Credits Attempted', 'count': 'Number of Students'},
                           title='Distribution of Credits Attempted',
                           color_discrete_sequence=['#e377c2'])
        st.plotly_chart(fig21, use_container_width=True)
    
    with col22:
        # Credits vs GPA
        sample_df2 = latest_df.sample(min(1000, len(latest_df)))
        fig22 = px.scatter(sample_df2, x='credits_attempted', y='cum_gpa',
                          color='pred_at_risk_flag',
                          labels={'credits_attempted': 'Credits Attempted',
                                 'cum_gpa': 'Cumulative GPA',
                                 'pred_at_risk_flag': 'Predicted At Risk'},
                          title='Credits Attempted vs GPA',
                          color_discrete_map={0: '#2ca02c', 1: '#d62728'},
                          opacity=0.6)
        st.plotly_chart(fig22, use_container_width=True)
    
    # 13. Residence Status Analysis
    st.markdown("#### Residence & Living Situation")
    col23, col24 = st.columns(2)
    
    with col23:
        # Residence Distribution
        residence_data = latest_df['residence'].value_counts()
        fig23 = px.pie(values=residence_data.values, names=residence_data.index,
                      title='Students by Residence Type',
                      color_discrete_sequence=px.colors.sequential.Sunset_r)
        st.plotly_chart(fig23, use_container_width=True)
    
    with col24:
        # At-Risk by Residence
        residence_risk = latest_df.groupby('residence')['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        residence_risk['percentage'] = (residence_risk['sum'] / residence_risk['count'] * 100).round(1)
        
        fig24 = px.bar(residence_risk, x='residence', y='percentage',
                      labels={'residence': 'Residence Type', 'percentage': 'At-Risk Percentage'},
                      title='At-Risk Percentage by Residence Type',
                      color='percentage',
                      color_continuous_scale='Reds',
                      text='percentage')
        fig24.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig24, use_container_width=True)
    
    # 14. Late Registration Impact
    st.markdown("#### Registration & Attendance Patterns")
    col25, col26 = st.columns(2)
    
    with col25:
        # Late Registration Impact
        late_reg_risk = latest_df.groupby('late_registration')['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        late_reg_risk['percentage'] = (late_reg_risk['sum'] / late_reg_risk['count'] * 100).round(1)
        
        fig25 = px.bar(late_reg_risk, x='late_registration', y='sum',
                      labels={'late_registration': 'Late Registration', 'sum': 'At-Risk Students'},
                      title='At-Risk Students by Registration Timing',
                      color='percentage',
                      color_continuous_scale='Oranges',
                      text='sum')
        fig25.update_xaxes(ticktext=['On-Time', 'Late Registration'], tickvals=[0, 1])
        fig25.update_traces(textposition='outside')
        st.plotly_chart(fig25, use_container_width=True)
    
    with col26:
        # Attendance vs Dropout Probability
        sample_df3 = latest_df.sample(min(1000, len(latest_df)))
        fig26 = px.scatter(sample_df3, x='attendance_rate', y='pred_dropout_probability',
                          color='pred_at_risk_flag',
                          labels={'attendance_rate': 'Attendance Rate (%)',
                                 'pred_dropout_probability': 'Predicted Dropout Probability',
                                 'pred_at_risk_flag': 'Predicted At Risk'},
                          title='Attendance Rate vs Predicted Dropout Probability',
                          color_discrete_map={0: '#2ca02c', 1: '#d62728'},
                          opacity=0.6)
        st.plotly_chart(fig26, use_container_width=True)
    
    # 15. Outstanding Balance Analysis
    st.markdown("#### Financial Balance & Risk Correlation")
    col27, col28 = st.columns(2)
    
    with col27:
        # Outstanding Balance Distribution
        balance_bins = pd.cut(latest_df['outstanding_balance'], 
                             bins=[-1, 0, 1000, 5000, 10000, 100000],
                             labels=['No Balance', '$1-1K', '$1K-5K', '$5K-10K', '$10K+'])
        balance_counts = balance_bins.value_counts().sort_index()
        
        fig27 = px.bar(x=balance_counts.index, y=balance_counts.values,
                      labels={'x': 'Outstanding Balance Range', 'y': 'Number of Students'},
                      title='Students by Outstanding Balance',
                      color=balance_counts.values,
                      color_continuous_scale='YlOrRd')
        st.plotly_chart(fig27, use_container_width=True)
    
    with col28:
        # Balance vs Risk
        fig28 = px.box(latest_df, x='pred_at_risk_flag', y='outstanding_balance',
                      labels={'pred_at_risk_flag': 'Predicted Risk Status', 'outstanding_balance': 'Outstanding Balance ($)'},
                      title='Outstanding Balance by Predicted Risk Status',
                      color='pred_at_risk_flag',
                      color_discrete_map={0: '#2ca02c', 1: '#d62728'})
        fig28.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0, 1])
        st.plotly_chart(fig28, use_container_width=True)
    
    # 16. Ethnicity Distribution
    st.markdown("#### Diversity & Inclusion Metrics")
    col29, col30 = st.columns(2)
    
    with col29:
        # Ethnicity Distribution
        ethnicity_data = latest_df['ethnicity'].value_counts().head(8)
        fig29 = px.bar(x=ethnicity_data.index, y=ethnicity_data.values,
                      labels={'x': 'Ethnicity', 'y': 'Number of Students'},
                      title='Student Distribution by Ethnicity',
                      color=ethnicity_data.values,
                      color_continuous_scale='Rainbow')
        fig29.update_xaxes(tickangle=45)
        st.plotly_chart(fig29, use_container_width=True)
    
    with col30:
        # At-Risk by Ethnicity
        ethnicity_risk = latest_df.groupby('ethnicity')['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        ethnicity_risk['percentage'] = (ethnicity_risk['sum'] / ethnicity_risk['count'] * 100).round(1)
        ethnicity_risk = ethnicity_risk.sort_values('sum', ascending=False).head(8)
        
        fig30 = px.bar(ethnicity_risk, x='ethnicity', y='sum',
                      labels={'ethnicity': 'Ethnicity', 'sum': 'At-Risk Students'},
                      title='At-Risk Students by Ethnicity',
                      color='percentage',
                      color_continuous_scale='Reds',
                      text='sum')
        fig30.update_xaxes(tickangle=45)
        fig30.update_traces(textposition='outside')
        st.plotly_chart(fig30, use_container_width=True)
    
    # 17. Age Distribution and Risk
    st.markdown("#### Age Analysis")
    col31, col32 = st.columns(2)
    
    with col31:
        # Age Distribution
        fig31 = px.histogram(latest_df, x='age',
                           nbins=25,
                           labels={'age': 'Student Age', 'count': 'Number of Students'},
                           title='Age Distribution of Students',
                           color_discrete_sequence=['#17becf'])
        st.plotly_chart(fig31, use_container_width=True)
    
    with col32:
        # Age vs Risk
        age_bins = pd.cut(latest_df['age'], bins=[0, 20, 25, 30, 35, 100],
                         labels=['Under 20', '20-25', '26-30', '31-35', '35+'])
        age_risk = latest_df.groupby(age_bins)['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        age_risk['percentage'] = (age_risk['sum'] / age_risk['count'] * 100).round(1)
        
        fig32 = px.bar(age_risk, x='age', y='percentage',
                      labels={'age': 'Age Group', 'percentage': 'At-Risk Percentage'},
                      title='At-Risk Percentage by Age Group',
                      color='percentage',
                      color_continuous_scale='Reds',
                      text='percentage')
        fig32.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig32, use_container_width=True)
    
    # 18. Correlation Heatmap
    st.markdown("#### Feature Correlation Analysis")
    
    # Select numeric columns for correlation
    numeric_cols = ['age', 'credits_attempted', 'course_drop_count', 'gpa_term', 'cum_gpa',
                   'lms_logins', 'attendance_rate', 'assignments_on_time_pct', 'discussion_posts',
                   'library_visits', 'work_hours_per_week', 'advisor_meetings', 'tutoring_sessions',
                   'pred_dropout_probability', 'pred_at_risk_flag']
    
    corr_matrix = latest_df[numeric_cols].corr()
    
    fig33 = px.imshow(corr_matrix,
                     labels=dict(color="Correlation"),
                     x=numeric_cols,
                     y=numeric_cols,
                     color_continuous_scale='RdBu_r',
                     aspect="auto",
                     title='Correlation Heatmap of Key Features')
    fig33.update_xaxes(tickangle=45)
    st.plotly_chart(fig33, use_container_width=True)


# -----------------------------
# STUDENT SEARCH PAGE
# -----------------------------
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
            risk_status = "🚨 AT RISK" if latest_record['pred_at_risk_flag']==1 else "✅ Not At Risk"
            st.metric("Risk Status", risk_status)
            
            st.markdown("#### Term-by-Term GPA Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=student_data['term'], y=student_data['gpa_term'], mode='lines+markers', name='Term GPA'))
            fig.add_trace(go.Scatter(x=student_data['term'], y=student_data['cum_gpa'], mode='lines+markers', name='Cumulative GPA'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No record found")
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
            page = st.radio("Select Page", ["Overview","At-Risk Students","At-Risk Students Data","Analytics","Student Search"])
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
        elif page=="At-Risk Students Data":
            display_at_risk_students_data(df)
        elif page=="Analytics":
            display_analytics(df)
        elif page=="Student Search":
            display_student_search(df)
        elif page=="Manual Prediction":
            display_manual_prediction(df)

if __name__=="__main__":
    main()
