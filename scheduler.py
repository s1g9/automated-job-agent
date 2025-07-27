import schedule
import time
import asyncio
from datetime import datetime
from typing import Callable
import threading

class JobScheduler:
    def __init__(self):
        self.jobs = []
        self.running = False
        self.thread = None
        
    def add_daily_job(self, func: Callable, time_str: str = "09:00"):
        """Add a job to run daily at specified time"""
        job = schedule.every().day.at(time_str).do(func)
        self.jobs.append(job)
        print(f"Scheduled job to run daily at {time_str}")
        
    def add_interval_job(self, func: Callable, minutes: int):
        """Add a job to run at specified interval"""
        job = schedule.every(minutes).minutes.do(func)
        self.jobs.append(job)
        print(f"Scheduled job to run every {minutes} minutes")
        
    def run_continuous(self):
        """Run the scheduler continuously in a separate thread"""
        def run():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        self.running = True
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        print("Scheduler started")
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        schedule.clear()
        print("Scheduler stopped")
        
    def run_once(self, func: Callable):
        """Run a job immediately"""
        try:
            func()
            print(f"Job executed successfully at {datetime.now()}")
        except Exception as e:
            print(f"Error executing job: {e}")