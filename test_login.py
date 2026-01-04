#!/usr/bin/env python3
"""
Quick test script to verify LinkedIn login with visible browser
This helps debug login issues by showing the browser window
"""

from scraper import JobScraper

print("=" * 60)
print("LinkedIn Login Test (Browser will be visible)")
print("=" * 60)
print("\nThis will:")
print("1. Open a browser window (visible)")
print("2. Navigate to LinkedIn login")
print("3. Attempt to login with your .env credentials")
print("4. Wait for you to complete any security verification")
print("\n" + "=" * 60 + "\n")

# Create scraper with headless=False (visible browser)
scraper = JobScraper(headless=False)

print("Starting LinkedIn login test...")
print("Watch the browser window that opens\n")

# Try to scrape (this will test login)
jobs = scraper.scrape_linkedin_jobs()

if jobs:
    print(f"\n✅ Success! Found {len(jobs)} jobs")
    print("\nFirst few jobs:")
    for job in jobs[:3]:
        print(f"  • {job['title']} at {job['company']}")
else:
    print("\n⚠️  No jobs found or login failed")
    print("\nCommon issues:")
    print("1. Check your .env file has correct LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
    print("2. LinkedIn may require manual security verification")
    print("   - Look for verification prompts in the browser window")
    print("   - Complete any CAPTCHA or email verification")
    print("3. Your LinkedIn account may have restricted automated access")

scraper.close()
