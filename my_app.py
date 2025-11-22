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
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import concurrent.futures



# ------------------------------
# THEME CONFIGURATION (GLOBAL)
# ------------------------------

THEME_COLORS = {
    "Light": {
        "bg": "#FFFFFF",
        "card": "#FFFFFF",
        "text": "#222222",
        "accent": "#FF7A00",
        "shadow": "rgba(0,0,0,0.12)"
    },
    "Dark": {
        "bg": "#1E1E1E",
        "card": "#2A2A2A",
        "text": "#ECECEC",
        "accent": "#FF8F33",
        "shadow": "rgba(255,255,255,0.1)"
    }
}

# -----------------------------------------
# GLOBAL PROFESSIONAL THEME + TYPOGRAPHY
# -----------------------------------------

st.markdown("""
<style>

/* IMPORT GOOGLE FONTS */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* PAGE BACKGROUND */
.main {
    padding: 1.8rem !important;
    background-color: #F7F7F9;
}

/* HEADINGS */
h1 {
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    color: #1A1A1A !important;
}

h2 {
    font-size: 1.9rem !important;
    font-weight: 600 !important;
    color: #222 !important;
}

h3 {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #333 !important;
}

/* PARAGRAPH TEXT */
p, label {
    font-size: 1rem !important;
    color: #2D2D2D !important;
}

/* CLEAN CARD DESIGN */
.block, .metric-card, .stDataFrame {
    background: #FFFFFF !important;
    border-radius: 14px !important;
    padding: 20px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
}

/* METRIC CARD STYLE */
.metric-card {
    height: 160px !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-left: 6px solid #FF7A00;
}

.metric-title {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #555 !important;
}

.metric-value {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #FF7A00 !important;
}

/* BUTTONS */
.stButton>button {
    background: linear-gradient(90deg, #FF7A00, #FF8F33) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.7rem 1.2rem !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 10px rgba(255,122,0,0.25) !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(255,122,0,0.35) !important;
}

/* INPUT FIELDS */
input, select, textarea {
    border-radius: 10px !important;
    border: 1px solid #DDD !important;
    padding: 10px !important;
}

/* EXPANDER STYLING */
.streamlit-expanderHeader {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
}

.streamlit-expanderHeader:hover {
    color: #FF7A00 !important;
}

/* DATAFRAME */
.stDataFrame div {
    font-size: 0.9rem !important;
}

            

.stButton>button {
    background: linear-gradient(90deg, #FF7A00, #FF8F33) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)



# -----------------------------
# CONFIG
# -----------------------------
EMAIL_USER = st.secrets["EMAIL"]["USER"]
EMAIL_PASS = st.secrets["EMAIL"]["PASS"]


#EMAIL_USER = "madhusonu7890@gmail.com"
#EMAIL_PASS = "szxu zfnd rogj nyqn"
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
                    st.rerun()
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
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

def send_email_async(to_addr, subject, body):
    """Send email asynchronously without blocking Streamlit UI."""
    def task():
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = to_addr
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            print(f"✅ Email sent to {to_addr}")
        except Exception as e:
            print(f"❌ Failed to send email to {to_addr}: {e}")

    executor.submit(task)

# -----------------------------
# RECOMMENDATION GENERATOR
# -----------------------------
def generate_recommendation(student):
    recs = []
    if student['cum_gpa'] < 2.5:
        recs.append("I recommend meeting with a tutor to strengthen your understanding of core subjects.")
    if student['attendance_rate'] < 80:
        recs.append("Please improve your class attendance, as it is affecting your overall performance.")
    if student['assignments_on_time_pct'] < 75:
        recs.append("I suggest working with a mentor to help you stay on track with assignment deadlines.")
    if student['course_drop_count'] > 0:
        recs.append("Let's review your course plan together to help you choose the right classes moving forward.")
    if student['probation_flag'] == 1:
        recs.append("I recommend scheduling an advising session to discuss your academic probation status")
    return recs

@st.cache_data
def get_recommendations(student_row):
    return generate_recommendation(student_row)


#----

def display_header():
    st.markdown(
        """
        <style>
        .dashboard-header {
            font-size: 38px;
            font-weight: 700;
            text-align: center;
            padding: 22px;
            margin-bottom: 25px;
            background: linear-gradient(90deg, #FF7A00, #FF8F33);
            color: #FFFFFF;
            border-radius: 14px;
            box-shadow: 0 6px 18px rgba(255, 122, 0, 0.35);
            letter-spacing: 0.5px;
            transition: 0.3s ease-in-out;
        }
        .dashboard-header:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 24px rgba(255, 122, 0, 0.45);
        }
        </style>

        <div class="dashboard-header">
            📊 Student Risk Monitoring Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# OVERVIEW PAGE
# -----------------------------
def display_overview(df):
    st.subheader("📊 Overview Metrics")

    # Latest record per student
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()

    # Metrics
    total_students = f"{latest_df['student_id'].nunique():,}"
    at_risk = f"{latest_df['pred_at_risk_flag'].sum():,}"
    low_att = f"{(latest_df['attendance_rate'] < 80).sum():,}"
    low_gpa = f"{(latest_df['cum_gpa'] < 2.0).sum():,}"
    probation = f"{latest_df['probation_flag'].sum():,}"

    # Colors matching your UI
    card_bg = "#FF6600"      # main orange
    card_title = "#FFFFFF"   # title text
    card_value = "#FFF3E0"   # value text

    # CSS for hover effect
    st.markdown(f"""
    <style>
        .metric-card {{
            background: {card_bg};
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            text-align: center;
            width: 100%;
            min-width: 150px;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }}
        .metric-title {{
            font-size: 18px;
            font-weight: 600;
            color: {card_title};
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: 800;
            color: {card_value};
        }}
    </style>
    """, unsafe_allow_html=True)

    # Columns for equal spacing
    cols = st.columns(5, gap="large")
    metrics = [
        ("Total Students", total_students),
        ("At-Risk Students", at_risk),
        ("Low Attendance (<80%)", low_att),
        ("Low GPA (<2.0)", low_gpa),
        ("On Probation", probation)
    ]

    for col, (title, value) in zip(cols, metrics):
        col.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)




# -----------------------------
# AT-RISK STUDENTS PAGE
# -----------------------------
# -----------------------------
# AT-RISK STUDENTS ALERT PAGE (Optimized + Async Email)
# -----------------------------
@st.cache_data
def preprocess_at_risk_students(df, threshold=0.3):
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()
    alert_df = latest_df[latest_df['pred_dropout_probability'] > threshold]
    alert_df['recommendations'] = alert_df.apply(lambda row: get_recommendations(row), axis=1)
    return alert_df

def display_at_risk(df, page_size=10):
    st.subheader("🚨 At-Risk Students with Pagination")

    threshold = st.slider("Minimum Dropout Probability (%)", 0, 100, 30, 5) / 100
    alert_df = preprocess_at_risk_students(df, threshold)
    total_students = len(alert_df)

    if total_students == 0:
        st.info(f"No students found with > {threshold*100:.0f}% dropout probability.")
        return

    # Pagination logic
    total_pages = (total_students - 1) // page_size + 1
    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size
    page_df = alert_df.iloc[start_idx:end_idx]

    st.warning(f"Showing {start_idx+1}–{min(end_idx, total_students)} of {total_students} students")

    for _, student in page_df.iterrows():
        with st.expander(f"👤 {student['student_id']} | GPA: {student['cum_gpa']:.2f} | Risk: {student['pred_dropout_probability']*100:.1f}%"):
            st.markdown(f"**Major:** {student['major']} | **Attendance:** {student['attendance_rate']:.1f}%")
            if student['recommendations']:
                st.markdown("**Recommendations:**")
                for r in student['recommendations']:
                    st.write(f"- {r}")

            email_input = st.text_input(f"Email for {student['student_id']}", key=f"email_{student['student_id']}")
            if st.button(f"📨 Send Email", key=f"send_{student['student_id']}"):
                if email_input:
                    body = (
                        f"Student ID: {student['student_id']}\n"
                        f"Major: {student['major']}\n"
                        f"GPA: {student['cum_gpa']:.2f}\n"
                        f"Attendance: {student['attendance_rate']:.1f}%\n"
                        f"Predicted Dropout Risk: {student['pred_dropout_probability']*100:.1f}%\n\n"
                        f"Recommendations:\n" + "\n".join(student['recommendations'])
                    )
                    send_email_async(email_input, "Student Recommendations", body)
                    st.info(f"📤 Email sent to {email_input}!")
                else:
                    st.warning("Please enter a valid email address.")



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
def display_kpi_cards(latest_df):
    total_students = len(latest_df)
    at_risk_students = latest_df['pred_at_risk_flag'].sum()
    avg_gpa = latest_df['cum_gpa'].mean()
    avg_attendance = latest_df['attendance_rate'].mean()
    risk_pct = (at_risk_students / total_students) * 100

    kpi_cards = [
        {"label": "Total Students", "value": total_students, "icon": "🎓", "color": "#A9D0F5"},  
        {"label": "At-Risk Students", "value": f"{at_risk_students} ({risk_pct:.1f}%)", "icon": "⚠️", "color": "#F5A9A9"},  
        {"label": "Average GPA", "value": f"{avg_gpa:.2f}", "icon": "📘", "color": "#A9F5A9"},  
        {"label": "Average Attendance", "value": f"{avg_attendance:.1f}%", "icon": "📊", "color": "#F5D0A9"},  
    ]

    # CSS for uniform size and dynamic text scaling
    hover_css = """
    <style>
    .kpi-card {
        width: 100%;
        height: 180px;  /* fixed height for all cards */
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 12px;
        color: #222;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card:hover {
        transform: scale(1.05);
        box-shadow: 4px 4px 20px rgba(0,0,0,0.3);
    }
    .kpi-card-icon {
        font-size: 2rem;
    }
    .kpi-card-value {
        font-size: clamp(1.2rem, 4vw, 1.8rem);  /* dynamic scaling */
        font-weight: bold;
        margin-top: 0.5rem;
        overflow-wrap: break-word;
    }
    .kpi-card-label {
        font-size: clamp(0.8rem, 2.5vw, 1rem);  /* dynamic scaling */
        margin-top: 0.3rem;
        font-weight: 600;
        overflow-wrap: break-word;
    }
    </style>
    """
    st.markdown(hover_css, unsafe_allow_html=True)

    cols = st.columns(len(kpi_cards), gap="large")
    for col, card in zip(cols, kpi_cards):
        col.markdown(
            f"""
            <div class="kpi-card" style="background-color:{card['color']}; color:#222;">
                <div class="kpi-card-icon">{card['icon']}</div>
                <div class="kpi-card-value">{card['value']}</div>
                <div class="kpi-card-label">{card['label']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )





import streamlit as st
import pandas as pd
import plotly.express as px

def display_analytics(df):
    st.subheader("📈 Student Analytics Dashboard")

    # Get latest data per student
    latest_df = df.sort_values('term').groupby('student_id').last().reset_index()

    # ------------------------
    # 1. KPI Summary Cards
    # ------------------------
    display_kpi_cards(latest_df)


    # ------------------------
    # 2. Tabs for organized charts
    # ------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Performance", "Engagement", "Demographics", "Financial & Risk"
    ])

    # ------------------------
    # Tab 1: Performance
    # ------------------------
    with tab1:
        st.markdown("### Attendance & GPA Distribution")
        fig1 = px.histogram(
            latest_df, x='attendance_rate', nbins=20,
            labels={'attendance_rate': 'Attendance Rate (%)', 'count': 'Number of Students'},
            color_discrete_sequence=['#1f77b4']
        )
        fig1.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="80% Threshold")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.histogram(
            latest_df, x='cum_gpa', nbins=20,
            labels={'cum_gpa': 'Cumulative GPA', 'count': 'Number of Students'},
            color_discrete_sequence=['#2ca02c']
        )
        fig2.add_vline(x=2.0, line_dash="dash", line_color="red", annotation_text="2.0 Threshold")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### At-Risk Students by Major")
        risk_by_major = latest_df.groupby('major')['pred_at_risk_flag'].agg(['sum', 'count']).reset_index()
        risk_by_major['percentage'] = (risk_by_major['sum']/risk_by_major['count']*100).round(1)
        risk_by_major = risk_by_major.sort_values('sum', ascending=True).tail(10)
        fig3 = px.bar(
            risk_by_major, x='sum', y='major', orientation='h',
            color='percentage', color_continuous_scale='Reds', text='sum',
            labels={'sum': 'Number of At-Risk Students', 'major': 'Major'}
        )
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### Assignment Completion vs GPA")
        sample_df = latest_df.sample(min(1000, len(latest_df)))
        fig4 = px.scatter(
            sample_df, x='assignments_on_time_pct', y='cum_gpa',
            color='pred_at_risk_flag',
            labels={'assignments_on_time_pct': 'Assignments On Time (%)',
                    'cum_gpa': 'Cumulative GPA', 'pred_at_risk_flag': 'Predicted At Risk'},
            color_discrete_map={0: '#2ca02c', 1: '#d62728'},
            opacity=0.6
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ------------------------
    # Tab 2: Engagement
    # ------------------------
    with tab2:
        st.markdown("### LMS & Advisor Engagement")
        fig8 = px.box(
            latest_df, x='pred_at_risk_flag', y='lms_logins',
            labels={'pred_at_risk_flag': 'Predicted Risk Status', 'lms_logins': 'LMS Logins'},
            color='pred_at_risk_flag', color_discrete_map={0: '#2ca02c', 1: '#d62728'}
        )
        fig8.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0,1])
        st.plotly_chart(fig8, use_container_width=True)

        fig9 = px.box(
            latest_df, x='pred_at_risk_flag', y='advisor_meetings',
            labels={'pred_at_risk_flag': 'Predicted Risk Status', 'advisor_meetings': 'Advisor Meetings'},
            color='pred_at_risk_flag', color_discrete_map={0: '#2ca02c', 1: '#d62728'}
        )
        fig9.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0,1])
        st.plotly_chart(fig9, use_container_width=True)

        with st.expander("Additional Engagement Metrics"):
            fig17 = px.box(latest_df, x='pred_at_risk_flag', y='tutoring_sessions',
                           color='pred_at_risk_flag', color_discrete_map={0: '#2ca02c', 1: '#d62728'},
                           labels={'pred_at_risk_flag': 'Predicted Risk Status', 'tutoring_sessions': 'Tutoring Sessions'})
            fig17.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0,1])
            st.plotly_chart(fig17, use_container_width=True)

            fig18 = px.box(latest_df, x='pred_at_risk_flag', y='library_visits',
                           color='pred_at_risk_flag', color_discrete_map={0: '#2ca02c', 1: '#d62728'},
                           labels={'pred_at_risk_flag': 'Predicted Risk Status', 'library_visits': 'Library Visits'})
            fig18.update_xaxes(ticktext=['Not At Risk', 'At Risk'], tickvals=[0,1])
            st.plotly_chart(fig18, use_container_width=True)

    # ------------------------
    # Tab 3: Demographics
    # ------------------------
    with tab3:
        st.markdown("### Gender, Enrollment & First Generation")
        col1, col2, col3 = st.columns(3)

        with col1:
            gender_data = latest_df['gender'].value_counts()
            fig14 = px.pie(values=gender_data.values, names=gender_data.index,
                           title='Students by Gender',
                           color_discrete_sequence=px.colors.sequential.Purples_r)
            st.plotly_chart(fig14, use_container_width=True)

        with col2:
            enrollment_data = latest_df['enrollment_status'].value_counts()
            fig15 = px.pie(values=enrollment_data.values, names=enrollment_data.index,
                           title='Enrollment Status',
                           color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig15, use_container_width=True)

        with col3:
            first_gen_data = latest_df['first_generation_flag'].value_counts()
            fig16 = px.pie(values=first_gen_data.values, names=['Not First Gen', 'First Generation'],
                           title='First Generation Status',
                           color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig16, use_container_width=True)

        st.markdown("### Age & Ethnicity")
        col4, col5 = st.columns(2)
        with col4:
            ethnicity_data = latest_df['ethnicity'].value_counts().head(8)
            fig29 = px.bar(x=ethnicity_data.index, y=ethnicity_data.values,
                           labels={'x': 'Ethnicity', 'y': 'Number of Students'},
                           title='Student Distribution by Ethnicity',
                           color=ethnicity_data.values, color_continuous_scale='Rainbow')
            fig29.update_xaxes(tickangle=45)
            st.plotly_chart(fig29, use_container_width=True)

        with col5:
            age_bins = pd.cut(latest_df['age'], bins=[0,20,25,30,35,100],
                              labels=['Under 20','20-25','26-30','31-35','35+'])
            age_risk = latest_df.groupby(age_bins)['pred_at_risk_flag'].agg(['sum','count']).reset_index()
            age_risk['percentage'] = (age_risk['sum']/age_risk['count']*100).round(1)
            fig32 = px.bar(age_risk, x='age', y='percentage', color='percentage',
                           color_continuous_scale='Reds', text='percentage',
                           labels={'age':'Age Group', 'percentage':'At-Risk %'})
            fig32.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig32, use_container_width=True)

    # ------------------------
    # Tab 4: Financial & Risk
    # ------------------------
    with tab4:
        st.markdown("### Financial Aid & Work Hours")
        col1, col2 = st.columns(2)

        with col1:
            financial_risk = latest_df.groupby('financial_aid_flag')['pred_at_risk_flag'].agg(['sum','count']).reset_index()
            financial_risk['percentage'] = (financial_risk['sum']/financial_risk['count']*100).round(1)
            fig12 = px.bar(financial_risk, x='financial_aid_flag', y='sum',
                           color='percentage', color_continuous_scale='Blues',
                           text='sum', labels={'financial_aid_flag':'Financial Aid Status','sum':'At-Risk Students'})
            fig12.update_xaxes(ticktext=['No Aid','Has Aid'], tickvals=[0,1])
            fig12.update_traces(textposition='outside')
            st.plotly_chart(fig12, use_container_width=True)

        with col2:
            work_bins = pd.cut(latest_df['work_hours_per_week'], bins=[-1,0,10,20,30,100],
                               labels=['Not Working','1-10','11-20','21-30','30+'])
            work_counts = work_bins.value_counts().sort_index()
            fig13 = px.bar(x=work_counts.index, y=work_counts.values,
                           color=work_counts.values, color_continuous_scale='Viridis',
                           labels={'x':'Work Hours','y':'Number of Students'},
                           title='Students by Work Hours')
            st.plotly_chart(fig13, use_container_width=True)

        st.markdown("### Dropout Probability Distribution")
        fig10 = px.histogram(latest_df, x='pred_dropout_probability', nbins=30,
                             labels={'pred_dropout_probability':'Predicted Dropout Probability','count':'Number of Students'},
                             title='Predicted Dropout Probability',
                             color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig10, use_container_width=True)

        with st.expander("Detailed Risk by Features"):
            numeric_cols = ['age','credits_attempted','course_drop_count','gpa_term','cum_gpa',
                            'lms_logins','attendance_rate','assignments_on_time_pct','discussion_posts',
                            'library_visits','work_hours_per_week','advisor_meetings','tutoring_sessions',
                            'pred_dropout_probability','pred_at_risk_flag']
            corr_matrix = latest_df[numeric_cols].corr()
            fig33 = px.imshow(corr_matrix, labels=dict(color="Correlation"), x=numeric_cols, y=numeric_cols,
                              color_continuous_scale='RdBu_r', aspect="auto", title='Correlation Heatmap')
            fig33.update_xaxes(tickangle=45)
            st.plotly_chart(fig33, use_container_width=True)



# -----------------------------
# STUDENT SEARCH PAGE
# -----------------------------
import streamlit as st
import plotly.graph_objects as go

def display_student_search(df):
    st.subheader("🔍 Student Search")
    search_id = st.text_input("Enter Student ID")
    
    if search_id:
        student_data = df[df['student_id'] == search_id]
        if not student_data.empty:
            latest_record = student_data.sort_values('term').iloc[-1]

            # Columns for circular indicators
            col1, col2, col3, col4 = st.columns(4)

            # GPA circular bar
            gpa_percent = (latest_record['cum_gpa'] / 4.0) * 100
            col1.markdown(f"""
            <div style="text-align:center;">
                <svg width="120" height="120">
                    <circle cx="60" cy="60" r="54" stroke="#e6e6e6" stroke-width="12" fill="none"/>
                    <circle cx="60" cy="60" r="54" stroke="#56ab2f" stroke-width="12" fill="none"
                        stroke-dasharray="{gpa_percent*3.39},339"
                        stroke-linecap="round" transform="rotate(-90 60 60)"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="#333">{latest_record['cum_gpa']:.2f}</text>
                </svg>
                <div style="margin-top:5px;">Cumulative GPA</div>
            </div>
            """, unsafe_allow_html=True)

            # Attendance circular bar
            att_percent = latest_record['attendance_rate']
            col2.markdown(f"""
            <div style="text-align:center;">
                <svg width="120" height="120">
                    <circle cx="60" cy="60" r="54" stroke="#e6e6e6" stroke-width="12" fill="none"/>
                    <circle cx="60" cy="60" r="54" stroke="#f7971e" stroke-width="12" fill="none"
                        stroke-dasharray="{att_percent*3.39},339"
                        stroke-linecap="round" transform="rotate(-90 60 60)"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="#333">{att_percent:.1f}%</text>
                </svg>
                <div style="margin-top:5px;">Attendance</div>
            </div>
            """, unsafe_allow_html=True)

            # Major circular badge
            col3.markdown(f"""
            <div style="text-align:center;">
                <svg width="120" height="120">
                    <circle cx="60" cy="60" r="54" stroke="#6DD5FA" stroke-width="12" fill="none"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="14" fill="#333">{latest_record['major']}</text>
                </svg>
                <div style="margin-top:5px;">Major</div>
            </div>
            """, unsafe_allow_html=True)

            # Risk Status circular bar based on predicted dropout probability
            risk_percent = latest_record['pred_dropout_probability'] * 100
            risk_color = "#FF4C4C" if risk_percent >= 50 else "#FFD166"
            risk_text = "🚨 AT RISK" if risk_percent >= 50 else "✅ Not At Risk"

            col4.markdown(f"""
            <div style="text-align:center;">
                <svg width="120" height="120">
                    <circle cx="60" cy="60" r="54" stroke="#e6e6e6" stroke-width="12" fill="none"/>
                    <circle cx="60" cy="60" r="54" stroke="{risk_color}" stroke-width="12" fill="none"
                        stroke-dasharray="{risk_percent*3.39},339"
                        stroke-linecap="round" transform="rotate(-90 60 60)"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="14" fill="#333">{risk_text}</text>
                </svg>
                <div style="margin-top:5px;">Risk Status</div>
            </div>
            """, unsafe_allow_html=True)

            # GPA Trend Chart
            st.markdown("#### Term-by-Term GPA Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=student_data['term'], y=student_data['gpa_term'],
                mode='lines+markers', name='Term GPA',
                marker=dict(size=10, color='#FFB347'),
                line=dict(width=3)
            ))
            fig.add_trace(go.Scatter(
                x=student_data['term'], y=student_data['cum_gpa'],
                mode='lines+markers', name='Cumulative GPA',
                marker=dict(size=10, color='#6A82FB'),
                line=dict(width=3, dash='dash')
            ))
            fig.update_layout(
                xaxis_title="Term",
                yaxis_title="GPA",
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )
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
                st.rerun()

        df = load_data()
        display_header() 
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


if __name__=="__main__":
    main()