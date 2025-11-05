# Quick Start Guide

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run streamlit_app.py
```

### Step 3: Create an Account & Login
1. Go to the "Sign Up" tab
2. Create your professor account
3. Login with your credentials

## What You'll See

### 📊 Overview Page
- Total students and at-risk counts
- Key metrics dashboard
- Quick summary of risk factors

### 🚨 At-Risk Students Page
- Complete list of at-risk students
- Filter by major, GPA, attendance
- Download data for offline analysis

### 📈 Analytics Page
- 11+ interactive charts and visualizations
- Attendance, GPA, engagement metrics
- Risk distribution across majors

### 🔍 Student Search Page
- Search any student by ID
- View complete academic history
- See term-by-term progress charts

## Quick Tips

✅ **Best Practice**: Check at-risk students weekly  
✅ **Use Filters**: Narrow down by specific criteria  
✅ **Export Data**: Download CSV for advisor meetings  
✅ **Track Progress**: Use student search for individual follow-ups  

## Common Questions

**Q: What makes a student "at-risk"?**  
A: The `at_risk_flag` in the dataset identifies students based on multiple factors including low attendance, poor GPA, high dropout probability, and low engagement metrics.

**Q: Can I see historical data?**  
A: Yes! Use the Student Search feature to view term-by-term progress for any student.

**Q: Can I export the data?**  
A: Yes! There's a download button on the At-Risk Students page.

**Q: How often is the data updated?**  
A: The dashboard reads from the CSV file. Update the CSV to see new data in the dashboard.

---

**Need help?** See the full README.md for detailed documentation.

