#!/usr/bin/env python3
"""Quick test of JobSpy integration"""

from job_search_v2 import JobSearcherV2
from notifier import JobNotifier
from job_tracker import JobTracker

def main():
    print("🧪 Testing JobSpy Integration...")
    
    searcher = JobSearcherV2()
    notifier = JobNotifier()
    tracker = JobTracker()
    
    preferred_locations = ['gurugram', 'gurgaon', 'delhi', 'new delhi', 'noida']
    
    print("🔍 Starting job search with JobSpy...")
    jobs = searcher.search_operations_jobs(
        preferred_locations=preferred_locations,
        min_salary_lpa=9,
        max_experience_years=2
    )
    
    if jobs:
        print(f"\n✅ Success! Found {len(jobs)} jobs")
        
        # Filter for new jobs
        new_jobs = tracker.filter_new_jobs(jobs, days_threshold=3)
        print(f"✨ New jobs: {len(new_jobs)}")
        
        # Save results
        if new_jobs:
            saved_file = notifier.save_jobs(new_jobs, "jobspy_test_results.json")
            html_report = notifier.create_html_report(new_jobs)
            
            print(f"💾 Saved to: {saved_file}")
            print(f"📄 HTML report: {html_report}")
            
            # Show sample results
            print(f"\n📋 Sample Jobs:")
            for i, job in enumerate(new_jobs[:3], 1):
                print(f"  {i}. {job['title']} at {job['company']}")
                print(f"     📍 {job['location']} | 💰 {job['salary']} | 🌐 {job['source']}")
                print(f"     🔗 {job['url'][:80]}...")
                print()
        
        tracker.record_daily_count(len(new_jobs))
        tracker.save_history()
        
    else:
        print("❌ No jobs found")

if __name__ == "__main__":
    main()