import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
import json
from datetime import datetime
import re

class IndeedScraper:
    """
    Simple Indeed scraper using requests and BeautifulSoup
    Based on research from multiple GitHub repositories
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def get_indeed_url(self, keyword: str, location: str, page: int = 0) -> str:
        """Construct Indeed search URL"""
        # Indeed uses 'start' parameter for pagination (10 jobs per page)
        start = page * 10
        
        # Indeed India URL format
        base_url = "https://in.indeed.com/jobs"
        params = {
            'q': keyword,
            'l': location,
            'start': start,
            'sort': 'date',  # Sort by date to get recent jobs
            'from': 'searchOnHP'  # Simulate coming from homepage
        }
        
        # Build URL with parameters
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def parse_job_card(self, card) -> Dict:
        """Extract job information from a job card element"""
        job = {}
        
        try:
            # Job title
            title_elem = card.find('h2', class_='jobTitle')
            if title_elem:
                title_link = title_elem.find('a') or title_elem.find('span')
                job['title'] = title_link.get_text(strip=True) if title_link else ''
                
                # Job URL
                if title_link and title_link.name == 'a':
                    job['url'] = 'https://in.indeed.com' + title_link.get('href', '')
                else:
                    job['url'] = ''
            
            # Company name
            company_elem = card.find('div', class_='company_location')
            if company_elem:
                company_name = company_elem.find('span', {'data-testid': 'company-name'})
                job['company'] = company_name.get_text(strip=True) if company_name else ''
                
                # Location
                location_elem = company_elem.find('div', {'data-testid': 'job-location'})
                job['location'] = location_elem.get_text(strip=True) if location_elem else ''
            
            # Salary
            salary_elem = card.find('div', class_='salary-snippet-container') or \
                         card.find('div', class_='metadata salary-snippet-container')
            job['salary'] = salary_elem.get_text(strip=True) if salary_elem else 'Not specified'
            
            # Job snippet/description
            snippet_elem = card.find('div', class_='job-snippet')
            job['description'] = snippet_elem.get_text(strip=True) if snippet_elem else ''
            
            # Posted date
            date_elem = card.find('span', class_='date')
            job['posted_date'] = date_elem.get_text(strip=True) if date_elem else ''
            
            # Source
            job['source'] = 'Indeed'
            job['scraped_date'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Error parsing job card: {e}")
            
        return job
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page of Indeed results"""
        jobs = []
        
        try:
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(2, 5))
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards - Indeed uses different class names
            job_cards = soup.find_all('div', class_='job_seen_beacon') or \
                       soup.find_all('div', class_='jobsearch-SerpJobCard') or \
                       soup.find_all('div', class_='result')
            
            print(f"Found {len(job_cards)} job cards on page")
            
            for card in job_cards:
                job = self.parse_job_card(card)
                if job.get('title'):  # Only add if we got a title
                    jobs.append(job)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
        except Exception as e:
            print(f"Error parsing page: {e}")
            
        return jobs
    
    def search_jobs(self, 
                   keywords: List[str], 
                   locations: List[str], 
                   max_pages: int = 3) -> List[Dict]:
        """
        Search for jobs on Indeed
        
        Args:
            keywords: List of job titles/keywords to search
            locations: List of locations to search in
            max_pages: Maximum number of pages to scrape per search
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        for keyword in keywords:
            for location in locations:
                print(f"\n🔍 Searching Indeed for '{keyword}' in '{location}'")
                
                for page in range(max_pages):
                    url = self.get_indeed_url(keyword, location, page)
                    print(f"  Scraping page {page + 1}...")
                    
                    jobs = self.scrape_page(url)
                    all_jobs.extend(jobs)
                    
                    # If we got no jobs, stop pagination
                    if not jobs:
                        print("  No more jobs found, moving to next search")
                        break
                    
                    print(f"  Found {len(jobs)} jobs on this page")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] and job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
            elif not job['url']:  # Keep jobs without URLs (they might be unique)
                unique_jobs.append(job)
        
        print(f"\n✅ Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs
    
    def filter_operations_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs for operations roles"""
        operations_keywords = [
            'operations', 'coordinator', 'executive', 'associate', 
            'analyst', 'admin', 'program', 'business operations'
        ]
        
        filtered_jobs = []
        for job in jobs:
            title_lower = job.get('title', '').lower()
            if any(keyword in title_lower for keyword in operations_keywords):
                filtered_jobs.append(job)
        
        return filtered_jobs


# Example usage for testing
if __name__ == "__main__":
    scraper = IndeedScraper()
    
    # Test with limited search
    jobs = scraper.search_jobs(
        keywords=['operations coordinator'],
        locations=['Gurugram', 'Delhi'],
        max_pages=1
    )
    
    # Save results
    with open('indeed_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Results saved to indeed_test_results.json")
    
    # Show sample results
    if jobs:
        print("\n📋 Sample job found:")
        job = jobs[0]
        print(f"Title: {job.get('title')}")
        print(f"Company: {job.get('company')}")
        print(f"Location: {job.get('location')}")
        print(f"Salary: {job.get('salary')}")