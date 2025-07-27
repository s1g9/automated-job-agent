from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
import uvicorn

from job_search import JobSearcher
from notifier import JobNotifier
from scheduler import JobScheduler
from job_tracker import JobTracker

# Load environment variables
load_dotenv()

app = FastAPI(title="Automated Job Search Agent", version="1.0.0")

# Initialize components
searcher = JobSearcher()
notifier = JobNotifier()
scheduler = JobScheduler()
tracker = JobTracker()

# Configuration from environment
MIN_SALARY_LPA = int(os.getenv('MIN_SALARY_LPA', '900000')) // 100000  # Convert to LPA
EXPERIENCE_LEVELS = os.getenv('EXPERIENCE_LEVEL', 'entry,fresher,0-1,0-2').split(',')
JOB_TITLES = os.getenv('JOB_TITLES', 'operations,operations coordinator').split(',')
LOCATION = os.getenv('LOCATION', 'India')
PREFERRED_LOCATIONS = os.getenv('PREFERRED_LOCATIONS', 'gurugram,gurgaon,delhi,new delhi,noida').split(',')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')

class JobSearchRequest(BaseModel):
    keywords: Optional[List[str]] = None
    min_salary_lpa: Optional[int] = None
    location: Optional[str] = None

class JobSearchResponse(BaseModel):
    total_jobs: int
    filtered_jobs: int
    jobs: List[dict]
    search_date: str
    report_file: Optional[str] = None

def perform_job_search():
    """Main job search function that runs daily"""
    print(f"Starting job search at {datetime.now()}")
    
    try:
        # Search across all platforms
        all_jobs = searcher.search_all_platforms(JOB_TITLES, LOCATION)
        print(f"Found {len(all_jobs)} total jobs")
        
        # Filter by location
        location_jobs = searcher.filter_by_location(all_jobs, PREFERRED_LOCATIONS)
        print(f"Found {len(location_jobs)} jobs in preferred locations: {', '.join(PREFERRED_LOCATIONS)}")
        
        # Filter by entry level
        entry_jobs = searcher.filter_entry_level(location_jobs)
        print(f"Found {len(entry_jobs)} entry-level jobs")
        
        # Filter by salary
        salary_jobs = searcher.filter_by_salary(entry_jobs, MIN_SALARY_LPA)
        print(f"Found {len(salary_jobs)} jobs matching criteria")
        
        # Filter out jobs we've seen recently
        filtered_jobs = tracker.filter_new_jobs(salary_jobs, days_threshold=3)
        print(f"Found {len(filtered_jobs)} NEW jobs (not seen in last 3 days)")
        
        # Record daily count
        tracker.record_daily_count(len(filtered_jobs))
        tracker.save_history()
        
        # Cleanup old history weekly
        if datetime.now().weekday() == 0:  # Monday
            tracker.cleanup_old_history()
        
        # Save results
        notifier.save_jobs(filtered_jobs)
        
        # Create HTML report
        if filtered_jobs:
            report_file = notifier.create_html_report(filtered_jobs)
            print(f"Created report: {report_file}")
            
        # Send email notification if configured
        if NOTIFICATION_EMAIL:
            notifier.send_email_notification(
                filtered_jobs, 
                NOTIFICATION_EMAIL,
                smtp_server=os.getenv('SMTP_SERVER'),
                smtp_port=int(os.getenv('SMTP_PORT', '587')),
                from_email=os.getenv('FROM_EMAIL'),
                password=os.getenv('EMAIL_PASSWORD')
            )
            
        return filtered_jobs
        
    except Exception as e:
        print(f"Error in job search: {e}")
        return []

@app.on_event("startup")
async def startup_event():
    """Schedule daily job searches on server startup"""
    # Schedule daily search at 9 AM
    scheduler.add_daily_job(perform_job_search, "09:00")
    
    # Also run every 6 hours for testing
    scheduler.add_interval_job(perform_job_search, 360)
    
    # Start the scheduler
    scheduler.run_continuous()
    
    print("Job search scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on server shutdown"""
    scheduler.stop()
    searcher.close()
    print("Server shutdown complete")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Automated Job Search Agent",
        "version": "1.0.0",
        "endpoints": {
            "/search": "Trigger manual job search",
            "/jobs": "Get latest job results",
            "/report": "Get latest HTML report",
            "/status": "Get system status"
        }
    }

@app.post("/search", response_model=JobSearchResponse)
async def manual_search(
    background_tasks: BackgroundTasks,
    request: JobSearchRequest = None
):
    """Manually trigger a job search"""
    # Use custom parameters or defaults
    keywords = request.keywords if request and request.keywords else JOB_TITLES
    min_salary = request.min_salary_lpa if request and request.min_salary_lpa else MIN_SALARY_LPA
    location = request.location if request and request.location else LOCATION
    
    # Perform search
    all_jobs = searcher.search_all_platforms(keywords, location)
    location_jobs = searcher.filter_by_location(all_jobs, PREFERRED_LOCATIONS)
    entry_jobs = searcher.filter_entry_level(location_jobs)
    filtered_jobs = searcher.filter_by_salary(entry_jobs, min_salary)
    
    # Save and create report
    notifier.save_jobs(filtered_jobs)
    report_file = None
    if filtered_jobs:
        report_file = notifier.create_html_report(filtered_jobs)
    
    return JobSearchResponse(
        total_jobs=len(all_jobs),
        filtered_jobs=len(filtered_jobs),
        jobs=filtered_jobs[:20],  # Return first 20 jobs
        search_date=datetime.now().isoformat(),
        report_file=str(report_file) if report_file else None
    )

@app.get("/jobs")
async def get_latest_jobs():
    """Get the latest job search results"""
    latest = notifier.load_latest_jobs()
    return latest

@app.get("/report")
async def get_latest_report():
    """Get the latest HTML report"""
    reports = list(notifier.storage_dir.glob("job_report_*.html"))
    if not reports:
        return {"error": "No reports available"}
        
    latest_report = max(reports, key=lambda p: p.stat().st_mtime)
    return FileResponse(latest_report, media_type="text/html")

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "scheduler_active": scheduler.running,
        "search_configuration": {
            "min_salary_lpa": MIN_SALARY_LPA,
            "job_titles": JOB_TITLES,
            "location": LOCATION,
            "experience_levels": EXPERIENCE_LEVELS
        },
        "last_search": notifier.load_latest_jobs().get('search_date', 'Never'),
        "total_saved_searches": len(list(notifier.storage_dir.glob("jobs_*.json")))
    }

@app.get("/trigger-search")
async def trigger_search_now(background_tasks: BackgroundTasks):
    """Immediately trigger a job search in the background"""
    background_tasks.add_task(perform_job_search)
    return {"message": "Job search triggered", "status": "running"}

if __name__ == "__main__":
    # Run the server
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', '8000'))
    
    print(f"Starting server on {host}:{port}")
    print(f"Searching for Operations jobs >={MIN_SALARY_LPA} LPA")
    print(f"Job titles: {', '.join(JOB_TITLES)}")
    
    uvicorn.run(app, host=host, port=port)