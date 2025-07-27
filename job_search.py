import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from datetime import datetime
import json
import time
import random
from urllib.parse import quote

class JobSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        self.session = httpx.Client(headers=self.headers, timeout=60.0, follow_redirects=True)
        
    def search_linkedin_jobs(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on LinkedIn (no login required for public job listings)"""
        jobs = []
        try:
            # LinkedIn public job search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote(keywords)}&location={quote(location)}&position=1&pageNum=0"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='base-card')[:20]
                
                for card in job_cards:
                    try:
                        # Extract job information
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        link_elem = card.find('a', class_='base-card__full-link')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': 'Check job description',
                                'experience': 'Check job description',
                                'url': link_elem.get('href', '') if link_elem else '',
                                'source': 'LinkedIn',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching LinkedIn: {e}")
            
        return jobs
    
    def search_indeed(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on Indeed India"""
        jobs = []
        try:
            # Indeed India URL
            base_url = "https://in.indeed.com/jobs"
            params = {
                'q': keywords,
                'l': location,
                'from': 'searchOnHP',
                'vjk': ''
            }
            
            response = self.session.get(base_url, params=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Different selectors for Indeed's current structure
                job_cards = soup.find_all('div', {'class': re.compile('job_seen_beacon|slider_container|jobsearch-SerpJobCard')})[:15]
                
                for card in job_cards:
                    try:
                        # Try multiple selectors as Indeed changes frequently
                        title_elem = card.find('h2', {'class': 'jobTitle'}) or card.find('a', {'data-testid': 'job-title'})
                        if title_elem:
                            title_span = title_elem.find('span', title=True)
                            title = title_span.get('title', '') if title_span else title_elem.text.strip()
                        else:
                            continue
                            
                        company_elem = card.find('span', {'data-testid': 'company-name'}) or card.find('span', {'class': 'companyName'})
                        location_elem = card.find('div', {'data-testid': 'job-location'}) or card.find('div', {'class': 'companyLocation'})
                        
                        # Extract salary if available
                        salary_elem = card.find('div', {'class': re.compile('salary-snippet|salaryOnly|salary')})
                        salary = salary_elem.text.strip() if salary_elem else 'Not disclosed'
                        
                        # Get job URL
                        link_elem = card.find('a', {'class': re.compile('jcs-JobTitle')}) or card.find('h2').find('a') if card.find('h2') else None
                        job_url = f"https://in.indeed.com{link_elem.get('href', '')}" if link_elem else ''
                        
                        if title and company_elem:
                            job = {
                                'title': title,
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': salary,
                                'experience': 'Entry level',
                                'url': job_url,
                                'source': 'Indeed',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Indeed: {e}")
            
        return jobs
    
    def search_glassdoor(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on Glassdoor"""
        jobs = []
        try:
            # Glassdoor search - using their job search page
            search_url = f"https://www.glassdoor.co.in/Job/india-{keywords.replace(' ', '-')}-jobs-SRCH_IL.0,5_IN115_KO6,{len(keywords)+6}.htm"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('li', {'class': re.compile('JobsList_jobListItem|react-job-listing')})[:15]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('a', {'class': re.compile('JobCard_jobTitle|job-title')})
                        company_elem = card.find('div', {'class': re.compile('EmployerProfile_employerName|job-employer')})
                        location_elem = card.find('div', {'class': re.compile('JobCard_location|job-location')})
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': 'Check job description',
                                'experience': 'Check job description',
                                'url': f"https://www.glassdoor.co.in{title_elem.get('href', '')}" if title_elem.get('href') else '',
                                'source': 'Glassdoor',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Glassdoor: {e}")
            
        return jobs
    
    def search_times_jobs(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on TimesJobs"""
        jobs = []
        try:
            # TimesJobs search URL
            search_url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={quote(keywords)}&txtLocation={quote(location)}"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('li', {'class': 'clearfix job-bx wht-shd-bx'})[:20]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('h3', {'class': 'joblist-comp-name'})
                        location_elem = card.find('ul', {'class': 'top-jd-dtl clearfix'})
                        
                        if title_elem and company_elem:
                            # Extract location from the details
                            loc_text = 'India'
                            if location_elem:
                                loc_span = location_elem.find('span', string=re.compile('Location'))
                                if loc_span:
                                    loc_text = loc_span.find_next_sibling(string=True)
                                    
                            # Extract experience
                            exp_text = 'Not specified'
                            if location_elem:
                                exp_li = location_elem.find('li', string=re.compile('card_travel'))
                                if exp_li:
                                    exp_text = exp_li.text.strip()
                            
                            # Get job URL
                            link_elem = title_elem.find('a')
                            
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': loc_text.strip() if loc_text else location,
                                'salary': 'Not disclosed',
                                'experience': exp_text,
                                'url': link_elem.get('href', '') if link_elem else '',
                                'source': 'TimesJobs',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching TimesJobs: {e}")
            
        return jobs
    
    def search_monster(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on Monster India"""
        jobs = []
        try:
            # Monster India search URL
            search_url = f"https://www.monsterindia.com/search/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-').lower()}"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='card-body')[:20]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='medium') or card.find('h3')
                        company_elem = card.find('div', class_='company-name') or card.find('a', class_='company-name')
                        location_elem = card.find('div', class_='loc-exp') or card.find('span', class_='location')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': 'Check job description',
                                'experience': 'Check job description',
                                'url': f"https://www.monsterindia.com{title_elem.find('a').get('href', '')}" if title_elem.find('a') else '',
                                'source': 'Monster',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Monster: {e}")
            
        return jobs
    
    def search_shine(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on Shine.com"""
        jobs = []
        try:
            # Shine search URL
            search_url = f"https://www.shine.com/job-search/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-').lower()}"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('div', class_='jobCard')[:20]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2') or card.find('a', class_='jobTitle')
                        company_elem = card.find('div', class_='recruiterName') or card.find('span', class_='company')
                        location_elem = card.find('div', class_='jobLocation') or card.find('span', class_='location')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': 'Not disclosed',
                                'experience': 'Entry level',
                                'url': f"https://www.shine.com{title_elem.find('a').get('href', '')}" if title_elem.find('a') else '',
                                'source': 'Shine',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Shine: {e}")
            
        return jobs
    
    def search_foundit(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on Foundit (formerly Monster)"""
        jobs = []
        try:
            # Foundit search URL
            search_url = f"https://www.foundit.in/jobs/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-').lower()}"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', {'class': re.compile('srpResultCard|job-card')})[:20]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3') or card.find('a', {'class': re.compile('jobTitle|job-title')})
                        company_elem = card.find('span', {'class': re.compile('companyName|company')})
                        location_elem = card.find('span', {'class': re.compile('location|jobLocation')})
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': 'Check job description',
                                'experience': 'Check job description',
                                'url': f"https://www.foundit.in{title_elem.get('href', '')}" if title_elem.get('href') else '',
                                'source': 'Foundit',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Foundit: {e}")
            
        return jobs
    
    def search_instahyre(self, keywords: str, location: str = "India") -> List[Dict]:
        """Search for jobs on Instahyre"""
        jobs = []
        try:
            # Instahyre search (they have an API-like structure)
            search_url = f"https://www.instahyre.com/search-jobs/?q={quote(keywords)}&l={quote(location)}"
            
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', {'class': re.compile('job-card|opportunity-card')})[:15]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h4') or card.find('h3')
                        company_elem = card.find('div', {'class': re.compile('company|employer')})
                        location_elem = card.find('span', {'class': re.compile('location|city')})
                        salary_elem = card.find('div', {'class': re.compile('salary|compensation')})
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'salary': salary_elem.text.strip() if salary_elem else 'Not disclosed',
                                'experience': 'Entry level',
                                'url': f"https://www.instahyre.com{title_elem.find('a').get('href', '')}" if title_elem.find('a') else '',
                                'source': 'Instahyre',
                                'scraped_date': datetime.now().isoformat()
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Instahyre: {e}")
            
        return jobs
    
    def filter_by_salary(self, jobs: List[Dict], min_salary_lpa: int) -> List[Dict]:
        """Filter jobs by minimum salary (in LPA)"""
        filtered_jobs = []
        
        for job in jobs:
            salary_text = job.get('salary', '').lower()
            
            # For now, include jobs where salary is not disclosed or needs checking
            # In real scenario, you'd need to visit each job page for details
            if 'not disclosed' in salary_text or 'check' in salary_text:
                # Include these for manual review
                filtered_jobs.append(job)
                continue
                
            # Try to extract salary amount
            if self._extract_salary_lpa(salary_text) >= min_salary_lpa:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _extract_salary_lpa(self, salary_text: str) -> float:
        """Extract salary in LPA from text"""
        salary_text = salary_text.lower()
        
        # Look for LPA mentions
        lpa_pattern = r'(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?)?\s*lpa'
        lpa_match = re.search(lpa_pattern, salary_text)
        if lpa_match:
            return float(lpa_match.group(1))
        
        # Look for lakh mentions
        lakh_pattern = r'(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?)?\s*(?:lakh|lac|l)'
        lakh_match = re.search(lakh_pattern, salary_text)
        if lakh_match:
            return float(lakh_match.group(1))
        
        # Look for annual salary in rupees
        annual_pattern = r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:-\s*\d+(?:,\d+)*(?:\.\d+)?)?\s*(?:per\s*)?(?:year|annual|p\.a\.)'
        annual_match = re.search(annual_pattern, salary_text)
        if annual_match:
            amount = float(annual_match.group(1).replace(',', ''))
            return amount / 100000  # Convert to lakhs
        
        return 0
    
    def filter_entry_level(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs suitable for entry-level/freshers"""
        filtered_jobs = []
        
        # Keywords that indicate entry level positions
        entry_keywords = ['entry', 'fresher', 'junior', '0-1', '0-2', 'graduate', 'beginner', 
                         'trainee', 'associate', 'coordinator', 'executive']
        
        # Keywords that indicate senior positions (to exclude)
        senior_keywords = ['senior', 'lead', 'manager', 'head', 'director', 'principal', 
                          'expert', 'specialist', '5+', '7+', '10+', 'years']
        
        for job in jobs:
            title = job.get('title', '').lower()
            experience = job.get('experience', '').lower()
            
            # Skip if it's clearly a senior position
            if any(keyword in title for keyword in senior_keywords):
                continue
                
            # Include if it matches entry level criteria
            if any(keyword in experience for keyword in entry_keywords) or \
               any(keyword in title for keyword in entry_keywords):
                filtered_jobs.append(job)
            elif re.search(r'0\s*-\s*[123]', experience):  # 0-1, 0-2, 0-3 years
                filtered_jobs.append(job)
            elif 'check' in experience or 'not specified' in experience:
                # Include for manual review if experience not specified
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def filter_by_location(self, jobs: List[Dict], preferred_locations: List[str]) -> List[Dict]:
        """Filter jobs by preferred locations"""
        filtered_jobs = []
        
        # Normalize location strings for comparison
        normalized_locations = [loc.lower().strip() for loc in preferred_locations]
        
        for job in jobs:
            job_location = job.get('location', '').lower()
            
            # Check if any preferred location is in the job location
            for preferred_loc in normalized_locations:
                if preferred_loc in job_location:
                    filtered_jobs.append(job)
                    break
                    
        return filtered_jobs
    
    def search_all_platforms(self, keywords: List[str], location: str = "India") -> List[Dict]:
        """Search across all job platforms with expanded coverage"""
        all_jobs = []
        
        # Define location variations for better coverage
        location_variations = [location]
        if location.lower() == "india":
            location_variations = ["India", "Delhi NCR", "NCR", "Gurgaon", "Gurugram"]
        
        # All search platforms
        platforms = [
            ("LinkedIn", self.search_linkedin_jobs),
            ("Indeed", self.search_indeed),
            ("TimesJobs", self.search_times_jobs),
            ("Monster", self.search_monster),
            ("Shine", self.search_shine),
            ("Foundit", self.search_foundit),
            ("Instahyre", self.search_instahyre)
        ]
        
        # Limit keywords to avoid too many searches (use first 8 most relevant)
        priority_keywords = keywords[:8]
        
        for keyword in priority_keywords:
            print(f"Searching for: {keyword}")
            
            # Try each location variation for better results
            for loc in location_variations[:2]:  # Use first 2 location variations
                print(f"  Location: {loc}")
                
                for platform_name, search_func in platforms:
                    try:
                        print(f"    - Searching {platform_name}...")
                        jobs = search_func(keyword, loc)
                        all_jobs.extend(jobs)
                        print(f"      Found {len(jobs)} jobs")
                        
                        # Random delay to avoid rate limiting
                        time.sleep(random.uniform(0.5, 2))
                        
                    except Exception as e:
                        print(f"      Error with {platform_name}: {e}")
                        continue
                
                # Delay between location searches
                time.sleep(random.uniform(1, 2))
        
        # Enhanced deduplication with fuzzy matching
        unique_jobs = self._deduplicate_jobs(all_jobs)
        
        print(f"\nTotal unique jobs found: {len(unique_jobs)}")
        return unique_jobs
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Enhanced deduplication with fuzzy matching"""
        unique_jobs = []
        seen_combinations = set()
        
        for job in jobs:
            # Create a more sophisticated key for deduplication
            title = job['title'].lower().strip()
            company = job['company'].lower().strip()
            location = job['location'].lower().strip()
            
            # Remove common words that might cause false negatives
            title_words = set(title.split())
            company_words = set(company.split())
            
            # Create a normalized key
            key = f"{'-'.join(sorted(title_words))}-{'-'.join(sorted(company_words))}"
            
            # Also check for exact title+company match
            exact_key = (title, company)
            
            if key not in seen_combinations and exact_key not in seen_combinations:
                seen_combinations.add(key)
                seen_combinations.add(exact_key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()