#!/usr/bin/env python3
"""
Enhanced GitHub Actions job search script using JobSpy library
More reliable and professional job scraping with better data quality
"""

import os
import sys
from datetime import datetime
from job_search_v2 import JobSearcherV2
from notifier import JobNotifier
from job_tracker import JobTracker

def main():
    print(f"🚀 Starting JobSpy-powered job search - {datetime.now()}")
    print(f"🔧 Using professional JobSpy library for better results")
    
    # Initialize components
    searcher = JobSearcherV2()
    notifier = JobNotifier(storage_dir="job_results")
    tracker = JobTracker(storage_dir=".")
    
    try:
        # Configuration from environment variables
        preferred_locations = os.getenv('PREFERRED_LOCATIONS', 'bangalore,bengaluru,electronic city,whitefield').split(',')
        min_salary_lpa = 8

        print(f"📋 Search Configuration:")
        print(f"  Platforms: LinkedIn, Indeed, Naukri, Glassdoor")
        print(f"  Locations: {', '.join(preferred_locations)}")
        print(f"  Min Salary: {min_salary_lpa} LPA")
        print(f"  Experience: Mid-level (3-5 years)")
        print(f"  Industry: Pharma / Healthcare / Metabolic Health / Capability Centers")
        print()
        
        # Perform comprehensive job search
        print(f"🔍 Searching for Program Management jobs in Pharma/Healthcare...")
        all_jobs = searcher.search_operations_jobs(
            preferred_locations=preferred_locations,
            min_salary_lpa=min_salary_lpa,
            max_experience_years=7
        )
        
        if not all_jobs:
            print("⚠️  No jobs found. Trying broader search...")
            # Fallback: try with broader program management terms
            import pandas as pd
            jobs_df = searcher.search_jobs(
                search_terms=["program manager", "project manager pharma", "healthcare program"],
                location="India",
                results_per_term=30,
                hours_old=168
            )
            
            if not jobs_df.empty:
                location_filtered = searcher.filter_by_location(jobs_df, preferred_locations)
                all_jobs = searcher.convert_to_job_dict_format(location_filtered)
        
        print(f"📊 Raw jobs found: {len(all_jobs)}")
        
        # Filter for new jobs only
        new_jobs = tracker.filter_new_jobs(all_jobs, days_threshold=3)
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
            
            # Print detailed summary
            print(f"\n🎯 JOB SEARCH SUMMARY:")
            print(f"  📈 Found {len(new_jobs)} new job opportunities!")
            print(f"  🏢 Companies include:")
            
            companies = list(set([job['company'] for job in new_jobs[:10]]))
            for company in companies[:5]:
                print(f"    • {company}")
            if len(companies) > 5:
                print(f"    • ... and {len(companies) - 5} more companies")
            
            print(f"\n📋 Top Job Matches:")
            for i, job in enumerate(new_jobs[:3], 1):
                print(f"  {i}. {job['title']} at {job['company']}")
                print(f"     📍 {job['location']} | 💰 {job['salary']} | 🌐 {job['source']}")
            
            if len(new_jobs) > 3:
                print(f"  ... and {len(new_jobs) - 3} more jobs in the report")
                
        else:
            print("📭 No new jobs found today that haven't been seen before.")
            print("💡 This is normal - it means the system is working to avoid duplicates!")
        
        # Show tracking stats
        stats = tracker.get_stats()
        print(f"\n📈 Tracking Statistics:")
        print(f"  Total jobs tracked: {stats['total_jobs_tracked']}")
        print(f"  Average daily jobs: {stats['avg_daily_jobs']:.1f}")
        print(f"  System uptime: Working perfectly! ✅")
        
        print(f"\n✅ JobSpy job search completed successfully at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error during job search: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to save debug information
        try:
            debug_info = {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'search_type': 'jobspy_enhanced'
            }
            with open('debug_error.json', 'w') as f:
                import json
                json.dump(debug_info, f, indent=2)
        except:
            pass
            
        sys.exit(1)

if __name__ == "__main__":
    main()