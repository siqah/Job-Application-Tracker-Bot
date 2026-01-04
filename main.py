import schedule
import time
from datetime import datetime, timedelta
from scraper import JobScraper
from application_bot import ApplicationBot
from tracker import ApplicationTracker
from notifications import NotificationManager
from reports import ReportGenerator
from database import ApplicationDatabase
from config import APPLICATION_SETTINGS

class JobApplicationManager:
    def __init__(self):
        self.scraper = JobScraper(headless=False)  # Set to True for production
        self.bot = ApplicationBot()
        self.tracker = ApplicationTracker()
        self.notifier = NotificationManager()
        self.reporter = ReportGenerator()
        self.db = ApplicationDatabase()
    
    def daily_routine(self):
        """Complete daily job search and application routine"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting Daily Routine - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Step 1: Scrape new jobs
        print("\n[1/5] 🔍 Scraping new jobs from LinkedIn...")
        jobs = self.scraper.scrape_linkedin_jobs()
        print(f"\n✓ Found {len(jobs)} new jobs")
        
        if not jobs:
            print("\nNo new jobs found. Skipping application step.")
            self._run_maintenance_tasks()
            return
        
        # Step 2: Save to database
        print("\n[2/5] 💾 Saving jobs to database...")
        saved_count = self.scraper.save_jobs_to_db(jobs)
        
        # Step 3: Apply to eligible jobs (if auto-apply enabled)
        print(f"\n[3/5] 📝 Processing applications...")
        print(f"Auto-apply enabled: {APPLICATION_SETTINGS['auto_apply']}")
        
        applications_today = 0
        max_apps = APPLICATION_SETTINGS['max_applications_per_day']
        
        if APPLICATION_SETTINGS['auto_apply']:
            print(f"Attempting to apply to up to {max_apps} jobs...")
            
            for job in jobs[:max_apps]:
                if applications_today >= max_apps:
                    break
                
                print(f"\n--- Application {applications_today + 1}/{max_apps} ---")
                result = self.bot.apply_to_job(job['url'], job)
                
                if result['status'] == 'applied':
                    applications_today += 1
                    self.db.update_status(job['url'], 'Applied')
                    if result.get('screenshot'):
                        self.db.update_screenshot(job['url'], result['screenshot'])
                    print(f"✅ Successfully applied!")
                    time.sleep(5)  # Be polite between applications
                
                elif result['status'] == 'manual_required':
                    self.db.update_status(job['url'], 'Manual Review Needed')
                    if result.get('screenshot'):
                        self.db.update_screenshot(job['url'], result['screenshot'])
                
                elif result['status'] == 'error':
                    self.db.update_status(job['url'], 'Application Error', result.get('error', ''))
                
                time.sleep(3)  # Delay between attempts
        else:
            print("ℹ️  Auto-apply disabled. Jobs saved for manual review.")
        
        # Update daily stats
        self.tracker.update_daily_stats(applications_sent=applications_today)
        
        # Run maintenance tasks
        self._run_maintenance_tasks()
        
        print(f"\n{'='*60}")
        print(f"✓ Daily Routine Completed!")
        print(f"  🔍 Jobs scraped: {len(jobs)}")
        print(f"  💾 Jobs saved: {saved_count}")
        print(f"  📝 Applications sent: {applications_today}")
        print(f"{'='*60}\n")
    
    def _run_maintenance_tasks(self):
        """Run follow-ups, interview checks, and reporting"""
        # Step 4: Check for follow-ups
        print("\n[4/5] 📬 Checking for follow-ups...")
        followups = self.tracker.check_followups()
        
        for followup in followups:
            self.notifier.send_followup_reminder(followup)
        
        # Step 5: Generate daily report
        print("\n[5/5] 📊 Generating daily report...")
        report_path = self.reporter.generate_daily_report()
        
        # Send report notification
        if report_path:
            self.notifier.send_daily_report(report_path)
    
    def monitor_interviews(self):
        """Check for upcoming interviews"""
        print(f"\n{'='*60}")
        print("📅 Checking upcoming interviews...")
        print(f"{'='*60}")
        
        upcoming = self.tracker.get_upcoming_interviews(days=2)
        
        for interview in upcoming:
            self.notifier.send_interview_reminder(interview)
        
        print(f"✓ Interview check completed\n")
    
    def weekly_review(self):
        """Generate weekly summary"""
        print(f"\n{'='*60}")
        print("📊 Generating weekly review...")
        print(f"{'='*60}")
        
        report_path = self.reporter.generate_weekly_report()
        self.notifier.send_weekly_report(report_path)
        
        # Print statistics
        self.tracker.get_stats_summary(days=7)
        
        print(f"\n✓ Weekly review completed\n")
    
    def show_stats(self, days=30):
        """Display statistics"""
        self.tracker.get_stats_summary(days)
    
    def list_applications(self, status=None, limit=20):
        """List recent applications"""
        if status:
            apps = self.db.get_applications_by_status(status)
            print(f"\n📋 Applications with status '{status}':")
        else:
            apps = self.db.get_all_applications(limit)
            print(f"\n📋 Recent applications (limit {limit}):")
        
        if not apps:
            print("   No applications found")
            return
        
        for app in apps:
            print(f"\n   • {app['job_title']} at {app['company_name']}")
            print(f"     Status: {app['application_status']} | Applied: {app['date_applied']}")
            print(f"     URL: {app['job_url']}")

def run_scheduler():
    """Setup scheduled tasks"""
    manager = JobApplicationManager()
    
    # Schedule daily job search (8 AM)
    schedule.every().day.at("08:00").do(manager.daily_routine)
    
    # Schedule interview checks (9 AM, 1 PM, 4 PM)
    schedule.every().day.at("09:00").do(manager.monitor_interviews)
    schedule.every().day.at("13:00").do(manager.monitor_interviews)
    schedule.every().day.at("16:00").do(manager.monitor_interviews)
    
    # Schedule weekly review (Monday 9 AM)
    schedule.every().monday.at("09:00").do(manager.weekly_review)
    
    print("⏰ Scheduler started. Press Ctrl+C to exit.\n")
    print("📅 Scheduled tasks:")
    for job in schedule.get_jobs():
        print(f"   • {job}")
    print()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

def interactive_menu():
    """Interactive CLI menu"""
    manager = JobApplicationManager()
    
    while True:
        print("\n" + "="*60)
        print("🎯 JOB APPLICATION TRACKER BOT")
        print("="*60)
        print("\n1. 🔍 Scrape jobs (no auto-apply)")
        print("2. 🚀 Run full daily routine")
        print("3. 📬 Check follow-ups")
        print("4. 📅 Check upcoming interviews")
        print("5. 📊 Generate daily report")
        print("6. 📈 Generate weekly report")
        print("7. 📋 List recent applications")
        print("8. 📊 View statistics")
        print("9. ⏰ Start scheduler (automated)")
        print("0. 🚪 Exit")
        
        choice = input("\nSelect an option (0-9): ").strip()
        
        if choice == "1":
            print("\n" + "="*60)
            jobs = manager.scraper.scrape_linkedin_jobs()
            if jobs:
                saved = manager.scraper.save_jobs_to_db(jobs)
                print(f"\n✓ Scraped and saved {saved} jobs")
        
        elif choice == "2":
            manager.daily_routine()
        
        elif choice == "3":
            followups = manager.tracker.check_followups()
            if followups:
                print(f"\nFound {len(followups)} applications needing follow-up")
        
        elif choice == "4":
            interviews = manager.tracker.get_upcoming_interviews(days=7)
            if interviews:
                print(f"\nFound {len(interviews)} upcoming interviews")
        
        elif choice == "5":
            report_path = manager.reporter.generate_daily_report()
            print(f"\n✓ Report generated: {report_path}")
        
        elif choice == "6":
            report_path = manager.reporter.generate_weekly_report()
            print(f"\n✓ Report generated: {report_path}")
        
        elif choice == "7":
            limit = input("How many applications to show? (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            manager.list_applications(limit=limit)
        
        elif choice == "8":
            days = input("Statistics for how many days? (default 30): ").strip()
            days = int(days) if days.isdigit() else 30
            manager.show_stats(days)
        
        elif choice == "9":
            print("\n⏰ Starting automated scheduler...")
            print("The bot will run automatically at scheduled times.")
            run_scheduler()
            break
        
        elif choice == "0":
            print("\n👋 Goodbye! Good luck with your job search!")
            break
        
        else:
            print("\n⚠️  Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command-line mode
        manager = JobApplicationManager()
        
        command = sys.argv[1].lower()
        
        if command == "scrape":
            jobs = manager.scraper.scrape_linkedin_jobs()
            manager.scraper.save_jobs_to_db(jobs)
            
        elif command == "apply":
            manager.daily_routine()
            
        elif command == "followups":
            manager.tracker.check_followups()
            
        elif command == "interviews":
            manager.monitor_interviews()
            
        elif command == "report":
            manager.reporter.generate_daily_report()
            
        elif command == "weekly":
            manager.weekly_review()
            
        elif command == "stats":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            manager.show_stats(days)
            
        elif command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            manager.list_applications(limit=limit)
            
        elif command == "scheduler":
            run_scheduler()
            
        else:
            print("Usage:")
            print("  python main.py scrape      - Scrape jobs only")
            print("  python main.py apply       - Run full application routine")
            print("  python main.py followups   - Check for follow-ups")
            print("  python main.py interviews  - Check upcoming interviews")
            print("  python main.py report      - Generate daily report")
            print("  python main.py weekly      - Generate weekly report")
            print("  python main.py stats [days] - View statistics")
            print("  python main.py list [limit] - List applications")
            print("  python main.py scheduler   - Run automated scheduler")
    else:
        # Interactive mode
        interactive_menu()
