import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH
from logger import get_logger

logger = get_logger(__name__)

class ApplicationDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary database tables"""
        cursor = self.conn.cursor()
        
        # Applications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            job_url TEXT UNIQUE,
            location TEXT,
            salary_range TEXT,
            date_applied DATE DEFAULT CURRENT_DATE,
            application_status TEXT DEFAULT 'Applied',
            status_updated DATE DEFAULT CURRENT_DATE,
            follow_up_date DATE,
            interview_date DATE,
            notes TEXT,
            resume_version TEXT,
            cover_letter_sent BOOLEAN DEFAULT FALSE,
            screenshot_path TEXT,
            date_posted DATE
        )
        ''')
        
        # Company contacts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            linkedin_url TEXT,
            last_contacted DATE
        )
        ''')
        
        # Daily stats table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date DATE PRIMARY KEY,
            applications_sent INTEGER DEFAULT 0,
            interviews_scheduled INTEGER DEFAULT 0,
            rejections_received INTEGER DEFAULT 0,
            offers_received INTEGER DEFAULT 0
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_url ON applications(job_url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON applications(application_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_applied ON applications(date_applied)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_followup_date ON applications(follow_up_date)')
        
        self.conn.commit()
        logger.debug("Database tables and indexes created successfully")
    
    def add_application(self, job_data):
        """Add a new job application to the database"""
        cursor = self.conn.cursor()
        
        # Calculate follow-up date (7 days from now)
        follow_up_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO applications 
            (job_title, company_name, job_url, location, salary_range, follow_up_date, date_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('url'),
                job_data.get('location'),
                job_data.get('salary', 'Not specified'),
                follow_up_date,
                job_data.get('date')
            ))
            
            self.conn.commit()
            logger.debug(f"Added application: {job_data.get('title')} at {job_data.get('company')}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Job already exists (duplicate URL)
            logger.debug(f"Job already in database: {job_data.get('url')}")
            return None
        except Exception as e:
            logger.error(f"Error adding application: {e}")
            return None
    
    def update_status(self, job_url, status, notes=""):
        """Update application status"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE applications 
        SET application_status = ?, status_updated = CURRENT_DATE, notes = ?
        WHERE job_url = ?
        ''', (status, notes, job_url))
        self.conn.commit()
    
    def update_screenshot(self, job_url, screenshot_path):
        """Update screenshot path for an application"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE applications 
        SET screenshot_path = ?
        WHERE job_url = ?
        ''', (screenshot_path, job_url))
        self.conn.commit()
    
    def get_pending_followups(self):
        """Get applications that need follow-up"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM applications 
        WHERE follow_up_date <= DATE('now') 
        AND application_status IN ('Applied', 'Interview Scheduled')
        ORDER BY follow_up_date ASC
        ''')
        return cursor.fetchall()
    
    def get_upcoming_interviews(self, days=7):
        """Get interviews happening within specified days"""
        cursor = self.conn.cursor()
        future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute('''
        SELECT * FROM applications 
        WHERE interview_date <= ? 
        AND interview_date >= DATE('now')
        AND application_status = 'Interview Scheduled'
        ORDER BY interview_date ASC
        ''', (future_date,))
        return cursor.fetchall()
    
    def get_daily_stats(self, date=None):
        """Get statistics for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date,))
        return cursor.fetchone()
    
    def update_daily_stats(self, date=None, **kwargs):
        """Update daily statistics"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        # Insert or update
        cursor.execute('''
        INSERT INTO daily_stats (date, applications_sent, interviews_scheduled, 
                                rejections_received, offers_received)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            applications_sent = applications_sent + ?,
            interviews_scheduled = interviews_scheduled + ?,
            rejections_received = rejections_received + ?,
            offers_received = offers_received + ?
        ''', (
            date,
            kwargs.get('applications_sent', 0),
            kwargs.get('interviews_scheduled', 0),
            kwargs.get('rejections_received', 0),
            kwargs.get('offers_received', 0),
            kwargs.get('applications_sent', 0),
            kwargs.get('interviews_scheduled', 0),
            kwargs.get('rejections_received', 0),
            kwargs.get('offers_received', 0)
        ))
        
        self.conn.commit()
    
    def get_all_applications(self, limit=100):
        """Get all applications with optional limit"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM applications 
        ORDER BY date_applied DESC 
        LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def get_applications_by_status(self, status):
        """Get applications filtered by status"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM applications 
        WHERE application_status = ?
        ORDER BY date_applied DESC
        ''', (status,))
        return cursor.fetchall()
    
    def get_stats_summary(self, days=30):
        """Get summary statistics for the past N days"""
        cursor = self.conn.cursor()
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
        SELECT 
            COUNT(*) as total_applications,
            SUM(CASE WHEN application_status = 'Interview Scheduled' THEN 1 ELSE 0 END) as interviews,
            SUM(CASE WHEN application_status = 'Rejected' THEN 1 ELSE 0 END) as rejections,
            SUM(CASE WHEN application_status = 'Offer' THEN 1 ELSE 0 END) as offers
        FROM applications
        WHERE date_applied >= ?
        ''', (start_date,))
        
        return cursor.fetchone()
    
    def close(self):
        """Close database connection"""
        self.conn.close()
