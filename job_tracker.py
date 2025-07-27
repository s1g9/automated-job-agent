import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Set
from pathlib import Path
import hashlib

class JobTracker:
    def __init__(self, storage_dir: str = "job_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.history_file = self.storage_dir / "job_history.json"
        self.load_history()
    
    def load_history(self):
        """Load job history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            else:
                self.history = {
                    "seen_jobs": {},  # job_hash: first_seen_date
                    "daily_counts": {},  # date: job_count
                    "last_cleanup": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error loading job history: {e}")
            self.history = {
                "seen_jobs": {},
                "daily_counts": {},
                "last_cleanup": datetime.now().isoformat()
            }
    
    def save_history(self):
        """Save job history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving job history: {e}")
    
    def generate_job_hash(self, job: Dict) -> str:
        """Generate a unique hash for a job based on title, company, and location"""
        job_string = f"{job['title'].lower().strip()}-{job['company'].lower().strip()}-{job.get('location', '').lower().strip()}"
        return hashlib.md5(job_string.encode()).hexdigest()
    
    def filter_new_jobs(self, jobs: List[Dict], days_threshold: int = 7) -> List[Dict]:
        """Filter out jobs we've seen in the last N days"""
        new_jobs = []
        current_date = datetime.now().date()
        threshold_date = current_date - timedelta(days=days_threshold)
        
        for job in jobs:
            job_hash = self.generate_job_hash(job)
            
            if job_hash in self.history["seen_jobs"]:
                # Check if we've seen this job recently
                first_seen = datetime.fromisoformat(self.history["seen_jobs"][job_hash]).date()
                if first_seen > threshold_date:
                    continue  # Skip this job, we've seen it recently
            
            # This is a new job or an old job we haven't seen recently
            new_jobs.append(job)
            self.history["seen_jobs"][job_hash] = datetime.now().isoformat()
        
        return new_jobs
    
    def record_daily_count(self, job_count: int):
        """Record the number of jobs found today"""
        today = datetime.now().date().isoformat()
        self.history["daily_counts"][today] = job_count
    
    def get_recent_daily_counts(self, days: int = 7) -> Dict[str, int]:
        """Get job counts for the last N days"""
        recent_counts = {}
        current_date = datetime.now().date()
        
        for i in range(days):
            date = (current_date - timedelta(days=i)).isoformat()
            recent_counts[date] = self.history["daily_counts"].get(date, 0)
        
        return recent_counts
    
    def cleanup_old_history(self, days_to_keep: int = 30):
        """Clean up job history older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean up seen_jobs
        jobs_to_remove = []
        for job_hash, date_str in self.history["seen_jobs"].items():
            if datetime.fromisoformat(date_str) < cutoff_date:
                jobs_to_remove.append(job_hash)
        
        for job_hash in jobs_to_remove:
            del self.history["seen_jobs"][job_hash]
        
        # Clean up daily_counts
        dates_to_remove = []
        for date_str, count in self.history["daily_counts"].items():
            if datetime.fromisoformat(date_str + "T00:00:00") < cutoff_date:
                dates_to_remove.append(date_str)
        
        for date_str in dates_to_remove:
            del self.history["daily_counts"][date_str]
        
        self.history["last_cleanup"] = datetime.now().isoformat()
        print(f"Cleaned up {len(jobs_to_remove)} old job records and {len(dates_to_remove)} old daily counts")
    
    def get_stats(self) -> Dict:
        """Get tracking statistics"""
        recent_counts = self.get_recent_daily_counts(7)
        total_jobs_tracked = len(self.history["seen_jobs"])
        
        return {
            "total_jobs_tracked": total_jobs_tracked,
            "recent_daily_counts": recent_counts,
            "avg_daily_jobs": sum(recent_counts.values()) / len(recent_counts) if recent_counts else 0,
            "last_cleanup": self.history.get("last_cleanup", "Never")
        }