#!/usr/bin/env python3
"""
Manual Job Entry Tool
Add jobs manually that you've applied to, bypassing LinkedIn scraping
"""

from database import ApplicationDatabase
from datetime import datetime, timedelta

def add_manual_application():
    """Interactively add a job application"""
    db = ApplicationDatabase()
    
    print("\n" + "="*60)
    print("📝 Add Job Application Manually")
    print("="*60 + "\n")
    
    # Get job details
    title = input("Job Title: ").strip()
    company = input("Company Name: ").strip()
    url = input("Job URL (optional): ").strip() or f"https://linkedin.com/jobs/manual_{datetime.now().timestamp()}"
    location = input("Location: ").strip()
    salary = input("Salary Range (optional): ").strip() or "Not specified"
    
    # Create job data
    job_data = {
        'title': title,
        'company': company,
        'url': url,
        'location': location,
        'salary': salary,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Preview
    print("\n" + "-"*60)
    print("Preview:")
    print(f"  Title: {title}")
    print(f"  Company: {company}")
    print(f"  Location: {location}")
    print(f"  Salary: {salary}")
    print("-"*60)
    
    confirm = input("\nSave this application? (y/n): ").strip().lower()
    
    if confirm == 'y':
        job_id = db.add_application(job_data)
        if job_id:
            print(f"\n✅ Application saved! (ID: {job_id})")
            print(f"Follow-up reminder set for: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}")
        else:
            print("\n❌ Failed to save application")
    else:
        print("\n❌ Cancelled")
    
    db.close()
    
    # Ask if they want to add another
    another = input("\nAdd another application? (y/n): ").strip().lower()
    if another == 'y':
        add_manual_application()

if __name__ == "__main__":
    try:
        add_manual_application()
        print("\n✨ Done! Use 'python3 main.py list' to see your applications")
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
