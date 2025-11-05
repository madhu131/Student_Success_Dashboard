# Student Risk Monitoring Dashboard

A comprehensive Streamlit web application designed for professors to monitor and identify at-risk students based on various academic and engagement metrics.

## Features

### 1. **Authentication System**
- Secure login and signup functionality for professors
- Password hashing using SHA256
- User credentials stored locally in `users.json`

### 2. **Overview Dashboard**
- Key metrics at a glance:
  - Total students count
  - Number of at-risk students
  - Students with low attendance (<80%)
  - Students with low GPA (<2.0)
  - Students on academic probation

### 3. **At-Risk Students Management**
- Dedicated view for students flagged as at-risk
- Advanced filtering options:
  - Filter by major
  - Filter by GPA threshold
  - Filter by attendance rate
- Detailed student information including:
  - Student ID, Major, Term
  - Cumulative GPA
  - Attendance rate
  - Assignment completion rate
  - Course drop count
  - Dropout probability
- Export functionality to download filtered data as CSV

### 4. **Analytics Dashboard**
Multiple interactive visualizations including:
- **Attendance Rate Distribution**: Histogram showing attendance patterns
- **GPA Distribution**: Cumulative GPA spread across students
- **At-Risk Students by Major**: Top majors with at-risk students
- **Assignment Completion vs GPA**: Scatter plot correlation
- **Students by Attendance Range**: Bar chart categorization
- **Course Drops Analysis**: Distribution of course drops
- **Probation Status**: Pie chart showing probation rates
- **LMS Engagement**: Box plots of LMS logins by risk status
- **Advisor Meetings**: Meeting frequency by risk status
- **Dropout Probability**: Distribution and risk level categorization

### 5. **Student Search**
- Search individual students by ID
- View comprehensive student profile:
  - Current major, GPA, attendance, and risk status
  - Term-by-term GPA trends (visual chart)
  - Complete academic history across all terms
  - Engagement metrics and support service usage

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone or navigate to the project directory**
```bash
cd /path/to/Assignments/Madhu
```

2. **Install required packages**
```bash
pip install -r requirements.txt
```

## Running the Application

1. **Ensure the data file exists**
   - Make sure `HSU_Student_Success_Data.csv` is in the same directory as `streamlit_app.py`

2. **Run the Streamlit app**
```bash
streamlit run streamlit_app.py
```

3. **Access the application**
   - The app will automatically open in your default browser
   - If not, navigate to: `http://localhost:8501`

## First Time Setup

1. **Create an account**
   - Go to the "Sign Up" tab
   - Enter username, email, and password (minimum 6 characters)
   - Click "Sign Up"

2. **Login**
   - Switch to the "Login" tab
   - Enter your credentials
   - Click "Login"

3. **Explore the dashboard**
   - Use the sidebar to navigate between different pages
   - View overview metrics, at-risk students, analytics, or search for specific students

## Dataset Structure

The application expects a CSV file with the following columns:
- `student_id`: Unique student identifier
- `term`: Academic term
- `age`, `gender`, `ethnicity`: Demographics
- `major`, `residence`, `enrollment_status`: Academic information
- `gpa_term`, `cum_gpa`: Academic performance
- `attendance_rate`: Attendance percentage
- `assignments_on_time_pct`: Assignment completion rate
- `course_drop_count`: Number of dropped courses
- `lms_logins`: Learning management system activity
- `advisor_meetings`, `tutoring_sessions`: Support services usage
- `dropout_probability`: Predicted dropout risk
- `at_risk_flag`: Binary flag (0 or 1) indicating at-risk status
- And other relevant metrics

## Key Risk Indicators

Students are flagged as "at-risk" based on multiple factors:
- Low attendance rate
- Poor academic performance (GPA)
- Low assignment completion percentage
- High course drop rate
- Low LMS engagement
- Academic probation status
- High dropout probability score

## Usage Tips

1. **Regular Monitoring**: Check the "At-Risk Students" page regularly to identify students needing intervention
2. **Use Filters**: Apply filters to narrow down specific cohorts or risk levels
3. **Export Data**: Download filtered lists for offline analysis or sharing with advisors
4. **Individual Follow-up**: Use the "Student Search" feature to review individual student progress
5. **Analytics Insights**: Review the analytics dashboard to identify systemic patterns and trends

## Security Notes

- User passwords are hashed using SHA256
- User data is stored in a local `users.json` file
- For production use, consider implementing:
  - Database storage for user credentials
  - More robust authentication (OAuth, JWT tokens)
  - HTTPS encryption
  - Session management improvements

## Troubleshooting

**Issue**: "Data file not found" error
- **Solution**: Ensure `HSU_Student_Success_Data.csv` is in the same directory as `streamlit_app.py`

**Issue**: Import errors
- **Solution**: Reinstall requirements: `pip install -r requirements.txt`

**Issue**: Port already in use
- **Solution**: Run with a different port: `streamlit run streamlit_app.py --server.port 8502`

**Issue**: Can't login after signup
- **Solution**: Make sure you're using the exact username and password. Check `users.json` to verify account creation.

## Future Enhancements

Potential features for future versions:
- Email notifications for at-risk students
- Integration with student information systems
- Machine learning model retraining interface
- Intervention tracking and outcome monitoring
- Mobile-responsive design improvements
- Role-based access control (admin, professor, advisor)
- Bulk student communication features

## Support

For issues or questions, please refer to the Streamlit documentation: https://docs.streamlit.io

---

**Last Updated**: November 2025

