from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
from pathlib import Path
from datetime import datetime
from config import APPLICATION_SETTINGS, RESUME_PATH, SCREENSHOTS_DIR, USER_INFO

class ApplicationBot:
    def __init__(self):
        self.resume_path = RESUME_PATH
        self.screenshots_dir = SCREENSHOTS_DIR
        self.user_info = USER_INFO
    
    def apply_to_job(self, job_url, job_details):
        """Apply to a single job posting"""
        print(f"\n📝 Applying to: {job_details['title']} at {job_details['company']}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=1000)  # Visible for debugging
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # Go to job page
                page.goto(job_url, timeout=30000)
                time.sleep(3)
                
                # Check if Easy Apply is available
                easy_apply_button = page.query_selector("button:has-text('Easy Apply')")
                
                if easy_apply_button and APPLICATION_SETTINGS['auto_apply']:
                    result = self._easy_apply(page, job_details)
                else:
                    # Take screenshot for manual application
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    company_safe = job_details['company'].replace(' ', '_').replace('/', '_')
                    screenshot_path = self.screenshots_dir / f"manual_{company_safe}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"   ℹ️  No Easy Apply available. Screenshot saved: {screenshot_path.name}")
                    result = {
                        "status": "manual_required",
                        "screenshot": str(screenshot_path),
                        "message": "Job requires manual application"
                    }
                    
            except Exception as e:
                print(f"   ❌ Error applying to job: {e}")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                company_safe = job_details.get('company', 'unknown').replace(' ', '_').replace('/', '_')
                screenshot_path = self.screenshots_dir / f"error_{company_safe}_{timestamp}.png"
                try:
                    page.screenshot(path=str(screenshot_path))
                except:
                    pass
                result = {"status": "error", "error": str(e), "screenshot": str(screenshot_path)}
            finally:
                browser.close()
            
            return result
    
    def _easy_apply(self, page, job_details):
        """Handle LinkedIn Easy Apply"""
        try:
            # Click Easy Apply
            page.click("button:has-text('Easy Apply')")
            time.sleep(2)
            
            # Handle multi-step application
            max_steps = 10
            current_step = 0
            
            while current_step < max_steps:
                current_step += 1
                print(f"   Processing step {current_step}...")
                
                # Check for phone number field
                phone_input = page.query_selector("input[id*='phoneNumber'], input[name*='phone']")
                if phone_input:
                    try:
                        phone_input.fill(self.user_info['phone'])
                        print(f"      ✓ Filled phone number")
                    except:
                        pass
                
                # Check for city/location field
                city_input = page.query_selector("input[id*='city'], input[name*='city']")
                if city_input:
                    try:
                        city_input.fill(self.user_info['city'])
                        print(f"      ✓ Filled city")
                    except:
                        pass
                
                # Check for resume upload
                resume_upload = page.query_selector("input[type='file']")
                if resume_upload and self.resume_path.exists():
                    try:
                        resume_upload.set_input_files(str(self.resume_path))
                        print(f"      ✓ Uploaded resume")
                        time.sleep(1)
                    except:
                        pass
                
                # Look for required fields that we can't fill automatically
                required_fields = page.query_selector_all("input[required]:not([type='file']):not([type='hidden'])")
                unfilled_required = [field for field in required_fields if not field.input_value()]
                
                if unfilled_required:
                    print(f"      ⚠️  {len(unfilled_required)} required fields need manual input")
                    # Take screenshot for manual completion
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    company_safe = job_details['company'].replace(' ', '_').replace('/', '_')
                    screenshot_path = self.screenshots_dir / f"manual_input_{company_safe}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    
                    return {
                        "status": "manual_required",
                        "screenshot": str(screenshot_path),
                        "message": f"Application requires manual input for {len(unfilled_required)} fields"
                    }
                
                # Look for next/review/submit button
                next_button = (
                    page.query_selector("button[aria-label*='Continue']:not([disabled])") or
                    page.query_selector("button[aria-label*='Review']:not([disabled])") or
                    page.query_selector("button[aria-label*='Next']:not([disabled])") or
                    page.query_selector("button:has-text('Next'):not([disabled])") or
                    page.query_selector("button:has-text('Review'):not([disabled])")
                )
                
                submit_button = (
                    page.query_selector("button[aria-label*='Submit application']:not([disabled])") or
                    page.query_selector("button:has-text('Submit application'):not([disabled])")
                )
                
                if submit_button:
                    # Final submit
                    print(f"      🎯 Submitting application...")
                    submit_button.click()
                    time.sleep(3)
                    
                    # Take success screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    company_safe = job_details['company'].replace(' ', '_').replace('/', '_')
                    screenshot_path = self.screenshots_dir / f"success_{company_safe}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    
                    print(f"   ✅ Application submitted successfully!")
                    return {
                        "status": "applied",
                        "screenshot": str(screenshot_path),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                
                elif next_button:
                    next_button.click()
                    time.sleep(2)
                else:
                    # No more buttons, might be done or stuck
                    print(f"      ⚠️  No next or submit button found")
                    break
            
            # If we get here, something went wrong
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_safe = job_details['company'].replace(' ', '_').replace('/', '_')
            screenshot_path = self.screenshots_dir / f"incomplete_{company_safe}_{timestamp}.png"
            page.screenshot(path=str(screenshot_path))
            
            return {
                "status": "incomplete",
                "screenshot": str(screenshot_path),
                "message": "Application flow incomplete"
            }
                
        except Exception as e:
            # Take error screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_safe = job_details.get('company', 'unknown').replace(' ', '_').replace('/', '_')
            screenshot_path = self.screenshots_dir / f"error_{company_safe}_{timestamp}.png"
            try:
                page.screenshot(path=str(screenshot_path))
            except:
                pass
            
            print(f"   ❌ Application error: {e}")
            return {"status": "error", "error": str(e), "screenshot": str(screenshot_path)}
