import time
import random
from typing import List, Dict
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

class IndeedSeleniumScraper:
    """
    Indeed scraper using Selenium for better reliability
    Based on successful implementations from GitHub research
    """
    
    def __init__(self, headless=True):
        self.setup_driver(headless)
        
    def setup_driver(self, headless=True):
        """Setup Chrome driver with anti-detection measures"""
        options = Options()
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance and stability options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        if headless:
            options.add_argument('--headless')
        
        # User agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Execute script to mask automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Make sure Chrome and ChromeDriver are installed")
            raise
    
    def get_indeed_url(self, keyword: str, location: str, start: int = 0) -> str:
        """Construct Indeed India search URL"""
        base_url = "https://in.indeed.com/jobs"
        params = f"?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}&start={start}"
        return base_url + params
    
    def extract_job_data(self, job_card) -> Dict:
        """Extract job information from a job card element"""
        job = {}
        
        try:
            # Job title
            try:
                title_elem = job_card.find_element(By.CSS_SELECTOR, 'h2.jobTitle a span[title]')
                job['title'] = title_elem.get_attribute('title')
                
                # Job URL
                link_elem = job_card.find_element(By.CSS_SELECTOR, 'h2.jobTitle a')
                job['url'] = link_elem.get_attribute('href')
            except:
                job['title'] = ''
                job['url'] = ''
            
            # Company name
            try:
                company_elem = job_card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]')
                job['company'] = company_elem.text
            except:
                job['company'] = ''
            
            # Location
            try:
                location_elem = job_card.find_element(By.CSS_SELECTOR, '[data-testid="job-location"]')
                job['location'] = location_elem.text
            except:
                job['location'] = ''
            
            # Salary
            try:
                salary_elem = job_card.find_element(By.CSS_SELECTOR, '[class*="salary-snippet"]')
                job['salary'] = salary_elem.text
            except:
                job['salary'] = 'Not specified'
            
            # Job snippet
            try:
                snippet_elem = job_card.find_element(By.CSS_SELECTOR, '.job-snippet')
                job['description'] = snippet_elem.text
            except:
                job['description'] = ''
            
            # Posted date
            try:
                date_elem = job_card.find_element(By.CSS_SELECTOR, '.date')
                job['posted_date'] = date_elem.text
            except:
                job['posted_date'] = ''
            
            job['source'] = 'Indeed'
            job['scraped_date'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            
        return job
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page of Indeed results"""
        jobs = []
        
        try:
            # Navigate to page
            self.driver.get(url)
            
            # Random delay to appear human
            time.sleep(random.uniform(3, 6))
            
            # Wait for job cards to load
            wait = WebDriverWait(self.driver, 10)
            
            # Check for different possible job card selectors
            job_cards = []
            selectors = [
                '.job_seen_beacon',
                '.jobsearch-SerpJobCard',
                '.result',
                '[data-jk]'  # Jobs have a data-jk attribute
            ]
            
            for selector in selectors:
                try:
                    cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                    if cards:
                        job_cards = cards
                        print(f"Found {len(job_cards)} job cards using selector: {selector}")
                        break
                except TimeoutException:
                    continue
            
            if not job_cards:
                print("No job cards found on page")
                return jobs
            
            # Extract data from each job card
            for card in job_cards:
                job = self.extract_job_data(card)
                if job.get('title'):  # Only add if we got a title
                    jobs.append(job)
            
            # Scroll to bottom to load any lazy-loaded content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error scraping page: {e}")
            
        return jobs
    
    def search_jobs(self, 
                   keywords: List[str], 
                   locations: List[str], 
                   max_results_per_search: int = 30) -> List[Dict]:
        """
        Search for jobs on Indeed using Selenium
        
        Args:
            keywords: List of job titles/keywords to search
            locations: List of locations to search in
            max_results_per_search: Maximum results per keyword/location combo
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        for keyword in keywords:
            for location in locations:
                print(f"\n🔍 Searching Indeed for '{keyword}' in '{location}'")
                
                results_collected = 0
                start = 0
                
                while results_collected < max_results_per_search:
                    url = self.get_indeed_url(keyword, location, start)
                    print(f"  Scraping page starting at result {start + 1}...")
                    
                    jobs = self.scrape_page(url)
                    
                    if not jobs:
                        print("  No more jobs found, moving to next search")
                        break
                    
                    all_jobs.extend(jobs)
                    results_collected += len(jobs)
                    print(f"  Found {len(jobs)} jobs on this page (total: {results_collected})")
                    
                    # Indeed shows 15 jobs per page
                    start += 15
                    
                    # Random delay between pages
                    time.sleep(random.uniform(2, 4))
        
        # Remove duplicates
        unique_jobs = []
        seen_urls = set()
        
        for job in all_jobs:
            if job['url'] and job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        print(f"\n✅ Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs
    
    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()


# Utility function to check if Selenium is properly set up
def check_selenium_setup():
    """Check if Selenium and ChromeDriver are properly installed"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        return True
    except Exception as e:
        print(f"Selenium setup error: {e}")
        return False


if __name__ == "__main__":
    # Check setup first
    if not check_selenium_setup():
        print("\n⚠️  Selenium is not properly set up.")
        print("Please install: pip install selenium")
        print("And download ChromeDriver from: https://chromedriver.chromium.org/")
    else:
        # Test the scraper
        print("✅ Selenium is properly set up. Testing scraper...")
        
        scraper = IndeedSeleniumScraper(headless=True)
        
        try:
            jobs = scraper.search_jobs(
                keywords=['operations coordinator'],
                locations=['Gurugram'],
                max_results_per_search=10
            )
            
            # Save results
            with open('indeed_selenium_test.json', 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 Results saved to indeed_selenium_test.json")
            
            # Show sample
            if jobs:
                print("\n📋 Sample job found:")
                job = jobs[0]
                print(f"Title: {job.get('title')}")
                print(f"Company: {job.get('company')}")
                print(f"Location: {job.get('location')}")
                print(f"Salary: {job.get('salary')}")
        
        finally:
            scraper.close()