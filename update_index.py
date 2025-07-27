#!/usr/bin/env python3
"""
Updates index.html to point to the latest job report
Run this script after each job search to update the main page
"""

import os
import glob
import re
from datetime import datetime
from pathlib import Path

def find_latest_report():
    """Find the most recent job report HTML file"""
    reports = glob.glob("job_results/job_report_*.html")
    if not reports:
        return None
    
    # Sort by modification time, most recent first
    reports.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return reports[0]

def extract_date_from_filename(filename):
    """Extract date from filename like job_report_20250724_235518.html"""
    match = re.search(r'job_report_(\d{8})_(\d{6})\.html', filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        
        hour = time_str[:2]
        minute = time_str[2:4]
        
        return f"{month}/{day}/{year} at {hour}:{minute}"
    return "Unknown"

def count_jobs_in_report(filepath):
    """Count number of jobs in the HTML report"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for job count in the summary
            match = re.search(r'Total Jobs Found:</strong> (\d+)', content)
            if match:
                return int(match.group(1))
    except:
        pass
    return 0

def update_index_html():
    """Update index.html with latest report information"""
    latest_report = find_latest_report()
    if not latest_report:
        print("No reports found")
        return
    
    # Extract info from latest report
    report_path = latest_report.replace('job_results/', '')
    report_date = extract_date_from_filename(latest_report)
    job_count = count_jobs_in_report(latest_report)
    
    # Read current index.html
    index_path = "index.html"
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the auto-redirect URL
    content = re.sub(
        r"window\.location\.href = '[^']+';",
        f"window.location.href = '{latest_report}';",
        content
    )
    
    # Update the redirect button
    content = re.sub(
        r"window\.location\.href = '[^']+';",
        f"window.location.href = '{latest_report}';",
        content
    )
    
    # Update latest report section
    latest_section = f'''    <div class="latest-report">
        <h2>📋 Latest Job Search Results</h2>
        <p><strong>Last Updated:</strong> {report_date}</p>
        <p><strong>Jobs Found:</strong> {job_count} matching positions</p>
        <a href="{latest_report}" class="view-latest-btn">
            View Latest Jobs Report 📊
        </a>
    </div>'''
    
    # Replace the latest report section
    content = re.sub(
        r'<div class="latest-report">.*?</div>',
        latest_section,
        content,
        flags=re.DOTALL
    )
    
    # Write updated content
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated index.html to point to latest report: {latest_report}")
    print(f"📊 Report date: {report_date}")
    print(f"💼 Jobs found: {job_count}")

if __name__ == "__main__":
    update_index_html()