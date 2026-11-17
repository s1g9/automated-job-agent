# Automated Job Search Agent

This system automatically searches for Program Management jobs in Pharma/Healthcare/Metabolic Health sectors daily that match specific criteria for Shivani Arora.

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
- ✅ Search multiple job platforms (LinkedIn, Naukri, Glassdoor, Indeed)
- ✅ Filter for Bangalore locations
- ✅ Find Program Management roles in Pharma/Healthcare >8 LPA
- ✅ Target mid-level positions (3-5 years experience)
- ✅ Save results to your GitHub repo
- ✅ Avoid duplicate jobs

### Option 2: Local Server

```bash
pip install -r requirements.txt
python main.py
```

## 📊 Features

### Job Search Coverage
- **4 Platforms**: LinkedIn, Indeed, Naukri, Glassdoor
- **15+ Keywords**: program manager, project manager, clinical program coordinator, healthcare program, pharma capability center, etc.
- **Industry Focus**: Pharma, Healthcare, Metabolic Health, Life Sciences, Capability Centers (GCC)
- **Smart Filtering**: Location, experience level (3-5 years), salary range (8+ LPA)
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
- **Experience**: Mid-level (3-5 years)
- **Current Salary**: 5.4 LPA
- **Target Salary**: Minimum 8 LPA
- **Location**: Bangalore, Bengaluru, Electronic City, Whitefield
- **Roles**: Program Manager, Project Manager, Program Coordinator, Clinical Program Manager, Medical Affairs Coordinator
- **Industries**: Metabolic Health, Pharma, Healthcare, Life Sciences, Biotech, Capability Centers (GCC)

## 📱 Manual Run

Test the search anytime:
```bash
python github_action_search.py
```

## 🔧 Configuration

Edit `.env` file:
```env
MIN_SALARY_LPA=800000
JOB_TITLES=program manager,project manager,program coordinator,clinical program coordinator
PREFERRED_LOCATIONS=bangalore,bengaluru,electronic city,whitefield
INDUSTRY_KEYWORDS=metabolic health,pharma,pharmaceutical,healthcare,capability center
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

**🎉 Ready to find your next Program Management opportunity in Pharma/Healthcare!**