from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
from datetime import datetime
from config import JOB_CRITERIA, LINKEDIN_CREDENTIALS
from database import ApplicationDatabase

class JobScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.db = ApplicationDatabase()
        self.credentials = LINKEDIN_CREDENTIALS
    
    def scrape_linkedin_jobs(self):
        """Scrape job listings from LinkedIn"""
        jobs_found = []
        
        if not self.credentials['email'] or not self.credentials['password']:
            print("⚠️  LinkedIn credentials not found in .env file")
            print("Please add LINKEDIN_EMAIL and LINKEDIN_PASSWORD to your .env file")
            return []
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=self.headless, slow_mo=500)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Login to LinkedIn
                print("🔐 Logging into LinkedIn...")
                if not self._linkedin_login(page):
                    print("❌ Login failed")
                    browser.close()
                    return []
                
                print("✓ Login successful")
                
                # Search for each keyword
                for keyword in JOB_CRITERIA['keywords']:
                    for location in JOB_CRITERIA['locations']:
                        print(f"\n🔍 Searching: {keyword} in {location}")
                        jobs = self._search_keyword(page, keyword, location)
                        jobs_found.extend(jobs)
                        print(f"   Found {len(jobs)} jobs")
                        time.sleep(2)  # Be polite between searches
                
                # Filter and deduplicate
                filtered_jobs = self._filter_jobs(jobs_found)
                print(f"\n✓ Total unique jobs after filtering: {len(filtered_jobs)}")
                
                browser.close()
                
            except Exception as e:
                print(f"❌ Error during scraping: {e}")
                return []
        
        return filtered_jobs
    
    
    def _linkedin_login(self, page):
        """Login to LinkedIn"""
        try:
            print("   → Navigating to LinkedIn login page...")
            page.goto("https://www.linkedin.com/login", timeout=30000)
            time.sleep(2)
            
            # Fill credentials
            print("   → Filling credentials...")
            page.fill("#username", self.credentials['email'])
            page.fill("#password", self.credentials['password'])
            
            print("   → Submitting login form...")
            page.click("button[type='submit']")
            time.sleep(3)
            
            # Wait for login to complete
            print("   → Waiting for login to complete...")
            try:
                page.wait_for_selector("nav.global-nav", timeout=15000)
                print("   ✓ Login successful!")
                time.sleep(2)
                return True
            except PlaywrightTimeoutError:
                # Check current URL for clues
                current_url = page.url
                print(f"   ⚠️  Login timeout. Current URL: {current_url}")
                
                # Check if security verification is required
                if "checkpoint" in current_url or "challenge" in current_url:
                    print("\n" + "="*60)
                    print("⚠️  LINKEDIN SECURITY VERIFICATION REQUIRED")
                    print("="*60)
                    print("\nLinkedIn detected automation and requires verification.")
                    print("Please check your email for a verification code or")
                    print("complete the CAPTCHA in the browser window (if visible).")
                    print("\nAfter completing verification, press Enter to continue...")
                    print("="*60 + "\n")
                    
                    input("Press Enter after completing verification: ")
                    
                    # Wait longer for manual verification
                    try:
                        page.wait_for_selector("nav.global-nav", timeout=60000)
                        print("   ✓ Verification completed! Login successful!")
                        return True
                    except PlaywrightTimeoutError:
                        print("   ❌ Still can't detect successful login")
                        print(f"   Current URL: {page.url}")
                        return False
                
                # Check if we're actually logged in despite timeout
                if "feed" in current_url or "mynetwork" in current_url:
                    print("   ✓ Appears to be logged in (on feed/network page)")
                    return True
                
                # Check for error messages
                error_elem = page.query_selector(".form__label--error, .error-text, .alert")
                if error_elem:
                    error_msg = error_elem.inner_text()
                    print(f"   ❌ Login error: {error_msg}")
                else:
                    print("   ❌ Login failed - no navigation detected")
                
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    
    def _search_keyword(self, page, keyword, location):
        """Search for jobs with specific keyword and location"""
        jobs = []
        
        try:
            # Build search URL (removed restrictive filters)
            search_url = (
                f"https://www.linkedin.com/jobs/search/?"
                f"keywords={keyword.replace(' ', '%20')}&"
                f"location={location.replace(' ', '%20')}"
            )
            
            page.goto(search_url, timeout=30000)
            
            # Wait for results to load
            try:
                page.wait_for_selector(".jobs-search__results-list", timeout=10000)
            except PlaywrightTimeoutError:
                print(f"   No results found for {keyword} in {location}")
                return []
            
            # Scroll to load more jobs
            for _ in range(3):
                page.mouse.wheel(0, 10000)
                time.sleep(1)
            
            # Extract job cards
            job_elements = page.query_selector_all(".job-search-card")
            
            for job_elem in job_elements[:15]:  # Limit to 15 per search
                try:
                    # Extract basic info
                    title_elem = job_elem.query_selector(".base-search-card__title")
                    company_elem = job_elem.query_selector(".base-search-card__subtitle")
                    location_elem = job_elem.query_selector(".job-search-card__location")
                    link_elem = job_elem.query_selector("a.base-card__full-link")
                    
                    if not all([title_elem, company_elem, location_elem, link_elem]):
                        continue
                    
                    job_data = {
                        'title': title_elem.inner_text().strip(),
                        'company': company_elem.inner_text().strip(),
                        'location': location_elem.inner_text().strip(),
                        'url': link_elem.get_attribute("href").split('?')[0],  # Remove query params
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    # Try to get time posted
                    try:
                        time_elem = job_elem.query_selector("time")
                        if time_elem:
                            job_data['date'] = time_elem.get_attribute("datetime")
                    except:
                        pass
                    
                    # Try to get salary if available
                    try:
                        salary_elem = job_elem.query_selector(".job-search-card__salary-info")
                        if salary_elem:
                            job_data['salary'] = salary_elem.inner_text().strip()
                        else:
                            job_data['salary'] = "Not specified"
                    except:
                        job_data['salary'] = "Not specified"
                    
                    jobs.append(job_data)
                    
                except Exception as e:
                    print(f"   Error extracting job: {e}")
                    continue
            
        except Exception as e:
            print(f"   Search error: {e}")
        
        return jobs
    
    def _filter_jobs(self, jobs):
        """Filter jobs based on criteria and remove duplicates"""
        filtered = []
        seen_urls = set()
        
        for job in jobs:
            # Deduplicate by URL
            if job['url'] in seen_urls:
                continue
            seen_urls.add(job['url'])
            
            # Check blacklist
            if any(blacklisted.lower() in job['company'].lower() 
                   for blacklisted in JOB_CRITERIA['blacklist_companies']):
                print(f"   ⊘ Skipping blacklisted company: {job['company']}")
                continue
            
            filtered.append(job)
        
        return filtered
    
    def save_jobs_to_db(self, jobs):
        """Save scraped jobs to database"""
        saved_count = 0
        for job in jobs:
            try:
                job_id = self.db.add_application(job)
                if job_id:
                    saved_count += 1
                    print(f"   ✓ Saved: {job['title']} at {job['company']}")
            except Exception as e:
                print(f"   ✗ Failed to save {job['title']}: {e}")
        
        print(f"\n📊 Saved {saved_count} new jobs to database")
        return saved_count
    
    def close(self):
        """Close database connection"""
        self.db.close()
