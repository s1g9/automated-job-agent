# Automated Job Search Agent

This system automatically searches for Operations jobs daily that match specific criteria for Shivani Arora.

## 🚀 Quick Setup (GitHub Actions - FREE)

### Option 1: GitHub Actions (Recommended - 100% Free)

1. **Create a GitHub repository** and upload this code
2. **Push to GitHub** - the workflow will automatically run daily at 9 AM IST
3. **View results** in the `job_results/` folder in your repo

```bash
# Upload to GitHub
git init
git add .
git commit -m "Initial job search agent"
git remote add origin https://github.com/yourusername/automated-job-agent.git
git push -u origin main
```

The system will automatically:
- ✅ Run daily at 9 AM IST
- ✅ Search 7 job platforms
- ✅ Filter for Gurugram/NCR locations
- ✅ Find entry-level operations roles >9 LPA
- ✅ Save results to your GitHub repo
- ✅ Avoid duplicate jobs

### Option 2: Local Server

```bash
pip install -r requirements.txt
python main.py
```

## 📊 Features

### Job Search Coverage
- **7 Platforms**: LinkedIn, Indeed, TimesJobs, Monster, Shine, Foundit, Instahyre
- **20+ Keywords**: operations coordinator, business operations, process coordinator, etc.
- **Smart Filtering**: Location, experience level, salary range
- **Duplicate Prevention**: Tracks seen jobs across days

### Automated Scheduling
- **Daily Search**: 9 AM IST every day
- **Results Storage**: JSON + HTML reports
- **Job Tracking**: Prevents showing same jobs repeatedly

### Output Files
```
job_results/
├── jobs_YYYYMMDD_HHMMSS.json      # Raw job data
├── job_report_YYYYMMDD_HHMMSS.html # Formatted report
└── job_history.json                # Tracking data
```

## 🎯 Search Criteria

Based on Shivani's profile:
- **Experience**: Entry level (0-2 years)
- **Salary**: Minimum 9 LPA
- **Location**: Gurugram, Gurgaon, Delhi, New Delhi, Noida, Faridabad
- **Roles**: Operations Coordinator, Operations Executive, Program Coordinator, etc.

## 📱 Manual Run

Test the search anytime:
```bash
python github_action_search.py
```

## 🔧 Configuration

Edit `.env` file:
```env
MIN_SALARY_LPA=900000
JOB_TITLES=operations,operations coordinator,business operations
PREFERRED_LOCATIONS=gurugram,gurgaon,delhi,new delhi,noida
```

## 📈 Expected Results

- **20-30 new jobs daily** across all platforms
- **5-15 matching jobs** after filtering
- **Zero duplicates** from previous days

## 🆓 Cost

- **GitHub Actions**: 100% Free (2,000 minutes/month included)
- **No server costs**
- **No maintenance required**

## 📧 Optional Email Notifications

Add to GitHub Secrets:
- `EMAIL_USERNAME`: Your Gmail
- `EMAIL_PASSWORD`: App password
- Set `SEND_EMAIL=true` in workflow

---

**🎉 Ready to find your next Operations opportunity!**