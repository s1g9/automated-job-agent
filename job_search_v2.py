import pandas as pd
from jobspy import scrape_jobs
from typing import List, Dict, Optional
from datetime import datetime
import re
import os
from indeed_scraper import IndeedScraper

class JobSearcherV2:
    """
    Enhanced job searcher using JobSpy library for better reliability and coverage
    """
    
    def __init__(self):
        self.supported_sites = [
            "indeed", "linkedin", "glassdoor", "google", "zip_recruiter", "naukri"
        ]
        
        # India-specific site configurations - Indeed removed from JobSpy due to issues
        self.india_sites = ["linkedin", "naukri", "glassdoor"]
        
        # Initialize Indeed scraper separately
        self.indeed_scraper = IndeedScraper()
        
    def search_jobs(self, 
                   search_terms: List[str],
                   location: str = "India",
                   results_per_term: int = 50,
                   hours_old: int = 168,  # 7 days
                   job_type: Optional[str] = None) -> pd.DataFrame:
        """
        Search for jobs using JobSpy across multiple platforms
        
        Args:
            search_terms: List of job titles/keywords to search
            location: Location to search in
            results_per_term: Number of results per search term
            hours_old: Only jobs posted within this many hours
            job_type: Type of job (fulltime, parttime, contract, etc.)
        
        Returns:
            DataFrame with all job results
        """
        all_jobs = []
        
        for term in search_terms:
            print(f"🔍 Searching for: {term}")
            
            try:
                # Search across multiple sites for each term
                jobs_df = scrape_jobs(
                    site_name=self.india_sites,
                    search_term=term,
                    location=location,
                    results_wanted=results_per_term,
                    hours_old=hours_old,
                    country_indeed='India',
                    job_type=job_type,
                    # linkedin_fetch_description=True,  # Enable for more details (slower)
                )
                
                if not jobs_df.empty:
                    # Add search term for tracking
                    jobs_df['search_term'] = term
                    jobs_df['scraped_date'] = datetime.now().isoformat()
                    all_jobs.append(jobs_df)
                    print(f"  ✅ Found {len(jobs_df)} jobs")
                else:
                    print(f"  ❌ No jobs found for: {term}")
                    
            except Exception as e:
                print(f"  ❌ Error searching for {term}: {e}")
                continue
        
        if all_jobs:
            # Combine all results
            combined_df = pd.concat(all_jobs, ignore_index=True)
            
            # Remove duplicates based on title, company, and location
            combined_df = combined_df.drop_duplicates(
                subset=['title', 'company', 'location'], 
                keep='first'
            )
            
            print(f"\n📊 Total unique jobs found: {len(combined_df)}")
            return combined_df
        else:
            print("\n❌ No jobs found across all search terms")
            return pd.DataFrame()
    
    def filter_by_location(self, jobs_df: pd.DataFrame, preferred_locations: List[str]) -> pd.DataFrame:
        """Filter jobs by preferred locations"""
        if jobs_df.empty:
            return jobs_df
            
        # Normalize locations for comparison
        normalized_locations = [loc.lower().strip() for loc in preferred_locations]
        
        def location_matches(job_location):
            if pd.isna(job_location):
                return False
            job_loc_lower = str(job_location).lower()
            return any(pref_loc in job_loc_lower for pref_loc in normalized_locations)
        
        filtered_df = jobs_df[jobs_df['location'].apply(location_matches)]
        print(f"📍 Jobs in preferred locations: {len(filtered_df)}")
        return filtered_df
    
    def filter_by_experience(self, jobs_df: pd.DataFrame, min_years: int = 3, max_years: int = 7) -> pd.DataFrame:
        """Filter for mid-level positions (3-7 years experience)"""
        if jobs_df.empty:
            return jobs_df

        # Keywords that indicate appropriate experience level
        target_keywords = [
            'associate', 'coordinator', 'analyst', 'program manager',
            'project manager', '3-5', '4-6', '3-7', '2-5', '4-7'
        ]

        # Keywords that indicate too senior positions (to exclude)
        senior_keywords = [
            'senior manager', 'head', 'director', 'vp', 'vice president',
            'principal', 'chief', '10+', '12+', '15+'
        ]

        # Keywords that indicate too junior (to exclude)
        junior_keywords = [
            'fresher', 'intern', 'trainee', 'entry level', '0-1', '0-2'
        ]

        def matches_experience(row):
            title = str(row.get('title', '')).lower()
            description = str(row.get('description', '')).lower()

            # Exclude clearly senior positions
            if any(keyword in title for keyword in senior_keywords):
                return False

            # Exclude too junior positions
            if any(keyword in title for keyword in junior_keywords):
                return False

            # Include if matches target criteria
            if any(keyword in title for keyword in target_keywords):
                return True

            # Look for specific year patterns in description
            exp_pattern = r'(\d+)\s*(?:-\s*(\d+))?\s*years?\s+(?:of\s+)?experience'
            exp_matches = re.findall(exp_pattern, description)
            if exp_matches:
                for match in exp_matches:
                    req_min = int(match[0])
                    req_max = int(match[1]) if match[1] else req_min + 2
                    # Check if her experience (4-5 years) falls within the range
                    if req_min <= 5 and req_max >= 3:
                        return True
                # If explicit requirements don't match, exclude
                if exp_matches:
                    return False

            return True  # Include by default if unclear

        filtered_df = jobs_df[jobs_df.apply(matches_experience, axis=1)]
        print(f"👤 Jobs matching experience level (3-7 years): {len(filtered_df)}")
        return filtered_df
    
    def filter_by_salary(self, jobs_df: pd.DataFrame, min_salary_lpa: int = 8) -> pd.DataFrame:
        """Filter jobs by minimum salary"""
        if jobs_df.empty:
            return jobs_df
            
        def meets_salary_requirement(row):
            min_amount = row.get('min_amount')
            max_amount = row.get('max_amount')
            interval = str(row.get('interval', '')).lower() if row.get('interval') is not None else ''
            description = str(row.get('description', '')).lower()
            
            # Convert LPA to appropriate amount based on interval
            target_amount = min_salary_lpa * 100000  # Convert LPA to rupees
            
            # Check explicit salary amounts
            if pd.notna(min_amount) and min_amount > 0:
                if interval == 'yearly':
                    return min_amount >= target_amount
                elif interval == 'monthly':
                    return (min_amount * 12) >= target_amount
                    
            # Check description for salary mentions
            salary_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?)?\s*lpa',
                r'(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?)?\s*(?:lakh|lac)',
                r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:-\s*\d+(?:,\d+)*(?:\.\d+)?)?\s*(?:per\s*)?(?:year|annual)'
            ]
            
            for pattern in salary_patterns:
                matches = re.findall(pattern, description)
                if matches:
                    try:
                        salary_value = float(matches[0].replace(',', ''))
                        if 'lpa' in pattern or 'lakh' in pattern:
                            return salary_value >= min_salary_lpa
                        else:  # Annual amount in rupees
                            return salary_value >= target_amount
                    except:
                        continue
                        
            # Include jobs with undisclosed salary for manual review
            return True
        
        filtered_df = jobs_df[jobs_df.apply(meets_salary_requirement, axis=1)]
        print(f"💰 Jobs meeting salary criteria: {len(filtered_df)}")
        return filtered_df
    
    def convert_to_job_dict_format(self, jobs_df: pd.DataFrame) -> List[Dict]:
        """Convert pandas DataFrame to list of job dictionaries for compatibility"""
        if jobs_df.empty:
            return []
            
        jobs_list = []
        for _, row in jobs_df.iterrows():
            job = {
                'title': str(row.get('title', 'Not specified')),
                'company': str(row.get('company', 'Not specified')),
                'location': str(row.get('location', 'Not specified')),
                'salary': self._format_salary(row),
                'experience': '3-5 years',  # Filtered for mid-level positions
                'url': str(row.get('job_url', '')),
                'source': str(row.get('site', 'JobSpy')).title(),
                'description': str(row.get('description', ''))[:500] + '...' if pd.notna(row.get('description')) else '',
                'job_type': str(row.get('job_type', 'Not specified')),
                'scraped_date': str(row.get('scraped_date', datetime.now().isoformat())),
                'search_term': str(row.get('search_term', ''))
            }
            jobs_list.append(job)
            
        return jobs_list
    
    def _format_salary(self, row) -> str:
        """Format salary information from JobSpy data"""
        min_amount = row.get('min_amount')
        max_amount = row.get('max_amount')
        interval = str(row.get('interval', '')) if row.get('interval') is not None else ''
        
        if pd.notna(min_amount) and pd.notna(max_amount):
            if interval.lower() == 'yearly':
                min_lpa = min_amount / 100000
                max_lpa = max_amount / 100000
                return f"{min_lpa:.1f}-{max_lpa:.1f} LPA"
            elif interval.lower() == 'monthly':
                min_lpa = (min_amount * 12) / 100000
                max_lpa = (max_amount * 12) / 100000
                return f"{min_lpa:.1f}-{max_lpa:.1f} LPA"
            else:
                return f"₹{min_amount:,.0f}-₹{max_amount:,.0f} {interval}"
        elif pd.notna(min_amount):
            if interval.lower() == 'yearly':
                min_lpa = min_amount / 100000
                return f"{min_lpa:.1f}+ LPA"
            else:
                return f"₹{min_amount:,.0f}+ {interval}"
        else:
            return "Check job description"
    
    def search_operations_jobs(self,
                             preferred_locations: List[str],
                             min_salary_lpa: int = 8,
                             max_experience_years: int = 3) -> List[Dict]:
        """
        Complete job search pipeline for program management roles in pharma/healthcare
        """
        # Search terms for program management in pharma/metabolic health
        search_terms = [
            "program manager pharma",
            "program manager healthcare",
            "project manager pharmaceutical",
            "program coordinator healthcare",
            "clinical program manager",
            "medical affairs coordinator",
            "program manager capability center",
            "associate program manager",
            "junior program manager",
            "program analyst healthcare",
            "project coordinator pharma",
            "program manager metabolic",
            "GCC program manager"
        ]
        
        all_jobs = []
        
        # 1. Search using JobSpy (LinkedIn, Naukri, Glassdoor)
        print("\n🔍 Searching with JobSpy (LinkedIn, Naukri, Glassdoor)...")
        jobs_df = self.search_jobs(
            search_terms=search_terms[:6],  # Limit to prevent timeout
            location="India",
            results_per_term=20,
            hours_old=168  # Last 7 days
        )
        
        if not jobs_df.empty:
            # Apply filters
            location_filtered = self.filter_by_location(jobs_df, preferred_locations)
            experience_filtered = self.filter_by_experience(location_filtered, min_years=3, max_years=max_experience_years)
            salary_filtered = self.filter_by_salary(experience_filtered, min_salary_lpa)
            
            # Convert to compatible format
            jobspy_jobs = self.convert_to_job_dict_format(salary_filtered)
            all_jobs.extend(jobspy_jobs)
            print(f"✅ JobSpy found {len(jobspy_jobs)} matching jobs")
        
        # 2. Search using custom Indeed scraper
        print("\n🔍 Searching with custom Indeed scraper...")
        try:
            indeed_jobs = self.indeed_scraper.search_jobs(
                keywords=search_terms[:3],  # Limit for speed
                locations=preferred_locations[:3],  # Top 3 locations
                max_pages=2  # 2 pages per search
            )
            
            # Filter for operations roles
            indeed_ops_jobs = self.indeed_scraper.filter_operations_jobs(indeed_jobs)
            
            # Convert Indeed format to standard format
            for job in indeed_ops_jobs:
                standardized_job = {
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'salary': job.get('salary', 'Check job description'),
                    'experience': '3-5 years',
                    'url': job.get('url', ''),
                    'source': 'Indeed',
                    'description': job.get('description', ''),
                    'job_type': 'Full-time',  # Default
                    'scraped_date': job.get('scraped_date', datetime.now().isoformat()),
                    'search_term': 'program management pharma'
                }
                
                # Basic salary filtering
                if self._job_meets_salary_requirement(standardized_job, min_salary_lpa):
                    all_jobs.append(standardized_job)
            
            print(f"✅ Indeed found {len([j for j in all_jobs if j['source'] == 'Indeed'])} matching jobs")
            
        except Exception as e:
            print(f"❌ Indeed scraper error: {e}")
            print("Continuing with results from other sources...")
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            key = (job['title'].lower().strip(), job['company'].lower().strip())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        print(f"\n🎯 Final results: {len(unique_jobs)} unique jobs matching all criteria")
        return unique_jobs
    
    def _job_meets_salary_requirement(self, job: Dict, min_salary_lpa: int) -> bool:
        """Check if a job meets the minimum salary requirement"""
        salary_text = job.get('salary', '').lower()
        
        # If salary not specified, include for manual review
        if not salary_text or salary_text == 'check job description' or 'not specified' in salary_text:
            return True
        
        # Look for LPA mentions
        lpa_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?)?\s*lpa',
            r'(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?)?\s*(?:lakh|lac)',
            r'₹\s*(\d+(?:,\d+)*)\s*(?:-\s*\d+(?:,\d+)*)?\s*(?:lakh|lac)'
        ]
        
        for pattern in lpa_patterns:
            matches = re.findall(pattern, salary_text)
            if matches:
                try:
                    salary_value = float(matches[0].replace(',', ''))
                    return salary_value >= min_salary_lpa
                except:
                    continue
        
        # Check for annual amounts
        annual_pattern = r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:-\s*\d+(?:,\d+)*(?:\.\d+)?)?\s*(?:per\s*)?(?:year|annual|p\.a\.)'
        matches = re.findall(annual_pattern, salary_text)
        if matches:
            try:
                annual_amount = float(matches[0].replace(',', ''))
                return annual_amount >= (min_salary_lpa * 100000)
            except:
                pass
        
        # If we can't determine, include it for manual review
        return True