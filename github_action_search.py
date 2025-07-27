#!/usr/bin/env python3
"""
GitHub Actions compatible job search script
Runs the job search and saves results without needing a persistent server
"""

import os
import sys
from datetime import datetime
from job_search import JobSearcher
from notifier import JobNotifier
from job_tracker import JobTracker

def main():
    print(f"🚀 Starting automated job search - {datetime.now()}")
    
    # Initialize components
    searcher = JobSearcher()
    notifier = JobNotifier(storage_dir="job_results")
    tracker = JobTracker(storage_dir=".")  # Store history in root
    
    try:
        # Configuration from environment variables
        job_titles = os.getenv('JOB_TITLES', 'operations,operations coordinator').split(',')
        location = os.getenv('LOCATION', 'India')
        preferred_locations = os.getenv('PREFERRED_LOCATIONS', 'gurugram,gurgaon,delhi').split(',')
        min_salary_lpa = 9
        
        print(f"📋 Search Configuration:")
        print(f"  Keywords: {len(job_titles)} terms")
        print(f"  Locations: {', '.join(preferred_locations)}")
        print(f"  Min Salary: {min_salary_lpa} LPA")
        print()
        
        # Search for jobs (use first 6 keywords to stay within time limits)
        priority_keywords = job_titles[:6]
        print(f"🔍 Searching with keywords: {priority_keywords}")
        
        all_jobs = searcher.search_all_platforms(priority_keywords, location)
        print(f"📊 Total jobs found: {len(all_jobs)}")
        
        if not all_jobs:
            print("⚠️  No jobs found. Trying fallback search...")
            all_jobs = searcher.search_all_platforms(['operations'], location)
        
        # Apply filters
        location_jobs = searcher.filter_by_location(all_jobs, preferred_locations)
        print(f"📍 Jobs in preferred locations: {len(location_jobs)}")
        
        entry_jobs = searcher.filter_entry_level(location_jobs)
        print(f"👤 Entry-level jobs: {len(entry_jobs)}")
        
        salary_jobs = searcher.filter_by_salary(entry_jobs, min_salary_lpa)
        print(f"💰 Jobs matching salary criteria: {len(salary_jobs)}")
        
        # Filter for new jobs only
        new_jobs = tracker.filter_new_jobs(salary_jobs, days_threshold=3)
        print(f"✨ NEW jobs (not seen in last 3 days): {len(new_jobs)}")
        
        # Record results
        tracker.record_daily_count(len(new_jobs))
        tracker.save_history()
        
        # Save results
        if new_jobs:
            saved_file = notifier.save_jobs(new_jobs)
            html_report = notifier.create_html_report(new_jobs)
            
            print(f"💾 Results saved to: {saved_file}")
            print(f"📄 HTML report: {html_report}")
            
            # Print summary
            print(f"\n🎯 SUMMARY:")
            print(f"  Found {len(new_jobs)} new job opportunities!")
            
            for i, job in enumerate(new_jobs[:5], 1):
                print(f"  {i}. {job['title']} at {job['company']} ({job['location']})")
            
            if len(new_jobs) > 5:
                print(f"  ... and {len(new_jobs) - 5} more jobs")
        else:
            print("📭 No new jobs found today. Check again tomorrow!")
        
        # Show tracking stats
        stats = tracker.get_stats()
        print(f"\n📈 Tracking Stats:")
        print(f"  Total jobs tracked: {stats['total_jobs_tracked']}")
        print(f"  Average daily jobs: {stats['avg_daily_jobs']:.1f}")
        
        print(f"\n✅ Job search completed successfully at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error during job search: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        searcher.close()

if __name__ == "__main__":
    main()