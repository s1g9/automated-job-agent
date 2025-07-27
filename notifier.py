import json
import os
from datetime import datetime
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

class JobNotifier:
    def __init__(self, storage_dir: str = "job_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
    def save_jobs(self, jobs: List[Dict], filename: str = None):
        """Save job results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.json"
            
        filepath = self.storage_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'search_date': datetime.now().isoformat(),
                'total_jobs': len(jobs),
                'jobs': jobs
            }, f, indent=2, ensure_ascii=False)
            
        print(f"Saved {len(jobs)} jobs to {filepath}")
        return filepath
    
    def load_latest_jobs(self) -> Dict:
        """Load the most recent job results"""
        files = list(self.storage_dir.glob("jobs_*.json"))
        if not files:
            return {'jobs': []}
            
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def format_job_summary(self, jobs: List[Dict]) -> str:
        """Format jobs into a readable summary"""
        if not jobs:
            return "No matching jobs found in today's search."
            
        summary = f"Found {len(jobs)} matching Operations jobs offering >9 LPA:\n\n"
        
        for i, job in enumerate(jobs[:10], 1):  # Show top 10
            summary += f"{i}. {job['title']}\n"
            summary += f"   Company: {job['company']}\n"
            summary += f"   Location: {job['location']}\n"
            summary += f"   Salary: {job['salary']}\n"
            summary += f"   Experience: {job['experience']}\n"
            summary += f"   Source: {job['source']}\n"
            summary += f"   URL: {job['url']}\n\n"
            
        if len(jobs) > 10:
            summary += f"\n... and {len(jobs) - 10} more jobs.\n"
            
        return summary
    
    def create_html_report(self, jobs: List[Dict]) -> str:
        """Create an HTML report of job listings"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Operations Job Search Results - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .job {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .job:hover {{ background-color: #f5f5f5; }}
                .job-title {{ font-size: 18px; font-weight: bold; color: #0066cc; }}
                .company {{ color: #666; margin: 5px 0; }}
                .details {{ margin: 10px 0; }}
                .apply-btn {{ background-color: #0066cc; color: white; padding: 8px 15px; 
                             text-decoration: none; border-radius: 3px; display: inline-block; }}
                .apply-btn:hover {{ background-color: #0052a3; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>Operations Job Search Results</h1>
            <div class="summary">
                <p><strong>Search Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p><strong>Total Jobs Found:</strong> {len(jobs)}</p>
                <p><strong>Criteria:</strong> Operations roles, >9 LPA, Entry level</p>
            </div>
        """
        
        for job in jobs:
            html += f"""
            <div class="job">
                <div class="job-title">{job['title']}</div>
                <div class="company">{job['company']} - {job['location']}</div>
                <div class="details">
                    <p><strong>Salary:</strong> {job['salary']}</p>
                    <p><strong>Experience:</strong> {job['experience']}</p>
                    <p><strong>Source:</strong> {job['source']}</p>
                </div>
                <a href="{job['url']}" target="_blank" class="apply-btn">View & Apply</a>
            </div>
            """
            
        html += """
        </body>
        </html>
        """
        
        # Save HTML report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = self.storage_dir / f"job_report_{timestamp}.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return str(html_file)
    
    def send_email_notification(self, jobs: List[Dict], to_email: str, 
                              smtp_server: str = None, smtp_port: int = 587,
                              from_email: str = None, password: str = None):
        """Send email notification with job results"""
        if not all([smtp_server, from_email, password]):
            print("Email configuration not provided. Skipping email notification.")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Operations Jobs Alert - {len(jobs)} new opportunities"
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Create text and HTML parts
            text_part = MIMEText(self.format_job_summary(jobs), 'plain')
            
            # Simple HTML version for email
            html_content = f"""
            <html>
            <body>
                <h2>Found {len(jobs)} Operations jobs matching your criteria</h2>
                <p>Jobs offering >9 LPA for entry-level positions:</p>
                <ul>
            """
            
            for job in jobs[:10]:
                html_content += f"""
                <li>
                    <strong>{job['title']}</strong> at {job['company']}<br>
                    Location: {job['location']}<br>
                    Salary: {job['salary']}<br>
                    <a href="{job['url']}">Apply Now</a>
                </li><br>
                """
                
            html_content += """
                </ul>
                <p>View the full report attached or check the job_results folder.</p>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(msg)
                
            print(f"Email notification sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False