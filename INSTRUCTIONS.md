# 📊 Student Risk Monitoring Dashboard - Running Instructions

## Prerequisites

Before running the dashboard, ensure you have:
- **Python 3.8 or higher** installed
- **pip** (Python package manager)
- The dataset file: `HSU_Student_Success_Data.csv` in the same directory

## Step-by-Step Instructions

### 1️⃣ **Navigate to the Project Directory**

Open your terminal and navigate to the project folder:

```bash
cd /Users/dheeraj/Desktop/Assignments/Madhu
```

Or if you're in a different location:

```bash
cd /path/to/your/project/directory
```

### 2️⃣ **Install Required Packages**

Install all dependencies using pip:

```bash
pip3 install -r requirements.txt
```

This will install:
- `streamlit` - Web application framework
- `pandas` - Data manipulation library
- `plotly` - Interactive visualization library

**Note**: If you encounter permission errors, try:
```bash
pip3 install --user -r requirements.txt
```

### 3️⃣ **Run the Streamlit Application**

Start the dashboard server:

```bash
streamlit run streamlit_app.py
```

**Alternative methods:**

If `streamlit` command is not found, try:
```bash
python3 -m streamlit run streamlit_app.py
```

Or use the full path:
```bash
/Users/dheeraj/Library/Python/3.9/bin/streamlit run streamlit_app.py
```

### 4️⃣ **Access the Dashboard**

Once the server starts, you'll see output like:

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.1.5:8501
```

The dashboard will **automatically open** in your default web browser. If it doesn't:

1. Open your browser manually
2. Go to: **http://localhost:8501**

### 5️⃣ **Create Your Account**

1. On the login page, click the **"Sign Up"** tab
2. Enter:
   - Username (e.g., `professor_smith`)
   - Email (e.g., `smith@university.edu`)
   - Password (minimum 6 characters)
   - Confirm Password
3. Click **"Sign Up"**
4. Go back to the **"Login"** tab

### 6️⃣ **Login to the Dashboard**

1. Enter your username and password
2. Click **"Login"**
3. You'll be redirected to the dashboard

### 7️⃣ **Navigate the Dashboard**

Use the **sidebar** to navigate between pages:

- **📊 Overview** - Key metrics and summary statistics
- **🚨 At-Risk Students** - Filtered list of students needing intervention
- **📈 Analytics** - 33 interactive visualizations and insights
- **🔍 Student Search** - Search individual students by ID

---

## 🎯 Quick Commands Reference

### Start the Dashboard
```bash
streamlit run streamlit_app.py
```

### Stop the Dashboard
Press `Ctrl + C` in the terminal

### Restart the Dashboard
If you make changes to the code:
1. Save your changes
2. Streamlit will automatically reload
3. Or restart manually: `Ctrl + C`, then run again

### Run on a Different Port
If port 8501 is busy:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Run in Headless Mode (No Browser Auto-Open)
```bash
streamlit run streamlit_app.py --server.headless true
```

---

## 🔧 Troubleshooting

### Issue: "streamlit: command not found"

**Solution**: Use the full Python module path:
```bash
python3 -m streamlit run streamlit_app.py
```

Or find where streamlit is installed:
```bash
pip3 show streamlit
```

### Issue: "Data file not found"

**Solution**: Ensure `HSU_Student_Success_Data.csv` is in the same directory as `streamlit_app.py`:
```bash
ls -la HSU_Student_Success_Data.csv
```

### Issue: Port Already in Use

**Solution**: Either stop the existing server or use a different port:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Issue: Import Errors

**Solution**: Reinstall dependencies:
```bash
pip3 uninstall streamlit pandas plotly
pip3 install -r requirements.txt
```

### Issue: Can't Login After Signup

**Solution**: 
1. Check if `users.json` was created in the directory
2. Ensure you're using the exact username and password
3. Try creating a new account with a different username

### Issue: Graphs Not Loading

**Solution**:
1. Check your internet connection (some fonts load from CDN)
2. Clear browser cache and refresh
3. Try a different browser

---

## 📱 Access from Other Devices

To access the dashboard from other devices on the same network:

1. Find the **Network URL** in the terminal output (e.g., `http://192.168.1.5:8501`)
2. On another device, open a browser and enter that URL
3. Make sure both devices are on the same network

---

## 🔐 Security Notes

- **First Use**: Create a professor account on first login
- **User Data**: Stored locally in `users.json` file
- **Passwords**: Automatically hashed using SHA256
- **Production Use**: Consider implementing more robust authentication for production environments

---

## 📊 Dashboard Features

### Overview Page
- Total student count
- At-risk student metrics
- Low attendance and GPA statistics
- Probation status summary

### At-Risk Students Page
- Complete list of flagged students
- Filter by major, GPA, attendance
- Download CSV for offline analysis
- Real-time filtering capabilities

### Analytics Page (33 Visualizations)
1. Attendance Rate Distribution
2. Cumulative GPA Distribution
3. At-Risk Students by Major
4. Assignment Completion vs GPA
5. Students by Attendance Range
6. Course Drop Analysis
7. Probation Status
8. LMS Logins by Risk Status
9. Advisor Meetings Analysis
10. Dropout Probability Distribution
11. Risk Level Categorization
12. Financial Aid Impact
13. Work Hours Distribution
14. Gender Distribution
15. Enrollment Status
16. First Generation Analysis
17. Tutoring Sessions
18. Library Visits
19. Discussion Posts Distribution
20. Discussion Posts by Risk
21. Credits Attempted
22. Credits vs GPA
23. Residence Distribution
24. At-Risk by Residence
25. Late Registration Impact
26. Attendance vs Dropout Probability
27. Outstanding Balance Distribution
28. Balance by Risk Status
29. Ethnicity Distribution
30. At-Risk by Ethnicity
31. Age Distribution
32. At-Risk by Age Group
33. Feature Correlation Heatmap

### Student Search Page
- Search by Student ID
- View complete academic history
- Term-by-term GPA trends
- Risk status and metrics

---

## 💡 Tips for Best Experience

1. **Use Chrome or Firefox** for best compatibility
2. **Full Screen Mode** - Press F11 for better visualization
3. **Export Data** - Use download buttons for offline analysis
4. **Regular Monitoring** - Check at-risk students weekly
5. **Filter Smart** - Use multiple filters to narrow down specific cohorts

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the main README.md file
3. Check Streamlit documentation: https://docs.streamlit.io

---

## 🚀 You're All Set!

Your dashboard is now ready to use. Access it at **http://localhost:8501** and start monitoring student success!

**Last Updated**: November 2025

