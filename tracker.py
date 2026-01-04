from datetime import datetime, timedelta
from database import ApplicationDatabase

class ApplicationTracker:
    def __init__(self):
        self.db = ApplicationDatabase()
    
    def check_followups(self):
        """Check for applications that need follow-up"""
        followups = self.db.get_pending_followups()
        
        if followups:
            print(f"\n📬 {len(followups)} follow-ups needed:")
            for app in followups:
                print(f"   • {app['job_title']} at {app['company_name']}")
                print(f"     Applied: {app['date_applied']} | Follow-up: {app['follow_up_date']}")
        else:
            print("\n✓ No follow-ups needed at this time")
        
        return followups
    
    def get_upcoming_interviews(self, days=7):
        """Get interviews happening within specified days"""
        interviews = self.db.get_upcoming_interviews(days)
        
        if interviews:
            print(f"\n📅 {len(interviews)} upcoming interviews:")
            for interview in interviews:
                print(f"   • {interview['job_title']} at {interview['company_name']}")
                print(f"     Date: {interview['interview_date']}")
        else:
            print(f"\n✓ No interviews scheduled in the next {days} days")
        
        return interviews
    
    def update_daily_stats(self, **kwargs):
        """Update statistics for today"""
        self.db.update_daily_stats(**kwargs)
    
    def get_stats_summary(self, days=30):
        """Get summary statistics"""
        stats = self.db.get_stats_summary(days)
        
        if stats:
            print(f"\n📊 Statistics for the last {days} days:")
            print(f"   Total Applications: {stats['total_applications']}")
            print(f"   Interviews: {stats['interviews']}")
            print(f"   Rejections: {stats['rejections']}")
            print(f"   Offers: {stats['offers']}")
            
            if stats['total_applications'] > 0:
                interview_rate = (stats['interviews'] / stats['total_applications']) * 100
                print(f"   Interview Rate: {interview_rate:.1f}%")
        
        return stats
    
    def update_application_status(self, job_url, new_status, notes=""):
        """Update the status of an application"""
        valid_statuses = ['Applied', 'Interview Scheduled', 'Rejected', 'Offer', 'Accepted', 'Declined']
        
        if new_status not in valid_statuses:
            print(f"⚠️  Invalid status: {new_status}")
            print(f"Valid statuses: {', '.join(valid_statuses)}")
            return False
        
        self.db.update_status(job_url, new_status, notes)
        print(f"✓ Updated status to: {new_status}")
        return True
    
    def schedule_interview(self, job_url, interview_date, notes=""):
        """Schedule an interview for an application"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        UPDATE applications 
        SET interview_date = ?, application_status = 'Interview Scheduled', notes = ?
        WHERE job_url = ?
        ''', (interview_date, notes, job_url))
        self.db.conn.commit()
        
        print(f"✓ Interview scheduled for: {interview_date}")
        return True
    
    def close(self):
        """Close database connection"""
        self.db.close()
