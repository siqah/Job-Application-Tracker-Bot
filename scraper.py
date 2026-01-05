from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import random
import json
from datetime import datetime
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import JOB_CRITERIA, LINKEDIN_CREDENTIALS, RETRY_SETTINGS, BROWSER_SETTINGS, SESSIONS_DIR
from database import ApplicationDatabase
from logger import get_logger

logger = get_logger(__name__)

class JobScraper:
    def __init__(self, headless=None):
        """Initialize job scraper with session management
        
        Args:
            headless: Override config headless setting (None uses config value)
        """
        self.headless = headless if headless is not None else BROWSER_SETTINGS['headless']
        self.db = ApplicationDatabase()
        self.credentials = LINKEDIN_CREDENTIALS
        self.session_file = SESSIONS_DIR / "linkedin_session.json"
        logger.info(f"JobScraper initialized (headless={self.headless})")
    
    def _human_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _save_session(self, context):
        """Save browser session (cookies) for reuse"""
        try:
            cookies = context.cookies()
            storage = context.storage_state()
            session_data = {
                'cookies': cookies,
                'storage': storage,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            logger.info("Browser session saved successfully")
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")
    
    def _load_session(self, context):
        """Load saved browser session if available"""
        if not self.session_file.exists():
            logger.debug("No saved session found")
            return False
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is recent (less than 7 days old)
            session_time = datetime.fromisoformat(session_data['timestamp'])
            age_days = (datetime.now() - session_time).days
            
            if age_days > 7:
                logger.info("Saved session is too old, will login again")
                return False
            
            # Add cookies to context
            context.add_cookies(session_data['cookies'])
            logger.info(f"Loaded session from {age_days} days ago")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(RETRY_SETTINGS['max_attempts']),
        wait=wait_exponential(
            multiplier=RETRY_SETTINGS['exponential_base'],
            min=RETRY_SETTINGS['wait_min'],
            max=RETRY_SETTINGS['wait_max']
        ),
        retry=retry_if_exception_type((PlaywrightTimeoutError, ConnectionError)),
        reraise=True
    )
    def scrape_linkedin_jobs(self):
        """Scrape job listings from LinkedIn with retry logic"""
        jobs_found = []
        
        if not self.credentials['email'] or not self.credentials['password']:
            logger.error("LinkedIn credentials not found in .env file")
            logger.info("Please add LINKEDIN_EMAIL and LINKEDIN_PASSWORD to your .env file")
            return []
        
        logger.info("Starting LinkedIn job scraping...")
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    headless=self.headless,
                    slow_mo=BROWSER_SETTINGS['slow_mo']
                )
                context = browser.new_context(
                    viewport={'width': 2560, 'height': 1600},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                # Try to load existing session
                session_loaded = self._load_session(context)
                
                # Login to LinkedIn (or verify session)
                logger.info("🔐 Logging into LinkedIn...")
                if not self._linkedin_login(page, skip_login=session_loaded):
                    logger.error("Login failed")
                    browser.close()
                    return []
                
                # Save session for future use
                self._save_session(context)
                
                logger.info("✓ Login successful")
                
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
    
    
    def _linkedin_login(self, page, skip_login=False):
        """Login to LinkedIn or verify existing session
        
        Args:
            page: Playwright page object
            skip_login: If True, try to skip login if session is loaded
        
        Returns:
            bool: True if login successful or session valid
        """
        try:
            if skip_login:
                # Try to verify session is still valid
                logger.info("   → Verifying saved session...")
                page.goto("https://www.linkedin.com/feed/", timeout=BROWSER_SETTINGS['timeout'])
                self._human_delay(2, 3)
                
                # Check if we're logged in
                try:
                    page.wait_for_selector("nav.global-nav", timeout=5000)
                    logger.info("   ✓ Session is valid, skipping login!")
                    return True
                except PlaywrightTimeoutError:
                    logger.warning("   ⚠️  Session expired, will login...")
            
            # Perform full login
            logger.info("   → Navigating to LinkedIn login page...")
            page.goto("https://www.linkedin.com/login", timeout=BROWSER_SETTINGS['timeout'])
            self._human_delay()
            
            # Fill credentials
            logger.info("   → Filling credentials...")
            page.fill("#username", self.credentials['email'])
            self._human_delay(0.5, 1.5)
            page.fill("#password", self.credentials['password'])
            
            logger.info("   → Submitting login form...")
            page.click("button[type='submit']")
            self._human_delay(2, 4)
            
            # Wait for login to complete
            logger.info("   → Waiting for login to complete...")
            try:
                page.wait_for_selector("nav.global-nav", timeout=15000)
                logger.info("   ✓ Login successful!")
                self._human_delay()
                return True
            except PlaywrightTimeoutError:
                # Check current URL for clues
                current_url = page.url
                logger.warning(f"   ⚠️  Login timeout. Current URL: {current_url}")
                
                # Check if security verification is required
                if "checkpoint" in current_url or "challenge" in current_url:
                    logger.warning("=" * 60)
                    logger.warning("⚠️  LINKEDIN SECURITY VERIFICATION REQUIRED")
                    logger.warning("=" * 60)
                    print("\nLinkedIn detected automation and requires verification.")
                    print("Please check your email for a verification code or")
                    print("complete the CAPTCHA in the browser window (if visible).")
                    print("\nAfter completing verification, press Enter to continue...")
                    print("=" * 60 + "\n")
                    
                    input("Press Enter after completing verification: ")
                    
                    # Wait longer for manual verification
                    try:
                        page.wait_for_selector("nav.global-nav", timeout=60000)
                        logger.info("   ✓ Verification completed! Login successful!")
                        return True
                    except PlaywrightTimeoutError:
                        logger.error("   ❌ Still can't detect successful login")
                        logger.error(f"   Current URL: {page.url}")
                        return False
                
                # Check if we're actually logged in despite timeout
                if "feed" in current_url or "mynetwork" in current_url:
                    logger.info("   ✓ Appears to be logged in (on feed/network page)")
                    return True
                
                # Check for error messages
                error_elem = page.query_selector(".form__label--error, .error-text, .alert")
                if error_elem:
                    error_msg = error_elem.inner_text()
                    logger.error(f"   ❌ Login error: {error_msg}")
                else:
                    logger.error("   ❌ Login failed - no navigation detected")
                
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Login error: {e}", exc_info=True)
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
