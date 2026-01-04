import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_SETTINGS

class NotificationManager:
    def __init__(self):
        self.settings = EMAIL_SETTINGS
        self.enabled = all([
            self.settings['email'],
            self.settings['password'],
            self.settings['smtp_server']
        ])
        
        if not self.enabled:
            print("⚠️  Email notifications disabled (credentials not configured)")
    
    def send_email(self, subject, body, html_body=None):
        """Send an email notification"""
        if not self.enabled:
            print(f"📧 [Email Disabled] Would send: {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.settings['email']
            msg['To'] = self.settings['email']
            msg['Subject'] = subject
            
            # Add text and HTML parts
            msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.settings['smtp_server'], self.settings['smtp_port']) as server:
                server.starttls()
                server.login(self.settings['email'], self.settings['password'])
                server.send_message(msg)
            
            print(f"✓ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_followup_reminder(self, application):
        """Send a follow-up reminder for an application"""
        subject = f"Follow-up Reminder: {application['job_title']}"
        body = f"""
It's time to follow up on your application!

Job: {application['job_title']}
Company: {application['company_name']}
Applied: {application['date_applied']}
Status: {application['application_status']}

Consider reaching out to the hiring manager or checking the application status.

Job URL: {application['job_url']}
"""
        
        return self.send_email(subject, body)
    
    def send_interview_reminder(self, interview):
        """Send an interview reminder"""
        subject = f"Interview Reminder: {interview['job_title']}"
        body = f"""
You have an upcoming interview!

Job: {interview['job_title']}
Company: {interview['company_name']}
Date: {interview['interview_date']}

Notes: {interview['notes'] or 'No notes'}

Good luck! 🎯
"""
        
        return self.send_email(subject, body)
    
    def send_daily_report(self, report_path):
        """Send daily application report"""
        subject = f"Daily Job Application Report - {datetime.now().strftime('%Y-%m-%d')}"
        body = f"""
Your daily job application report is ready!

Report location: {report_path}

Keep up the great work! 💪
"""
        
        return self.send_email(subject, body)
    
    def send_weekly_report(self, report_path):
        """Send weekly application summary"""
        subject = f"Weekly Job Application Summary - {datetime.now().strftime('%Y-%m-%d')}"
        body = f"""
Your weekly job application summary is ready!

Report location: {report_path}

Review your progress and adjust your strategy as needed! 📊
"""
        
        return self.send_email(subject, body)
    
    def send_application_notification(self, job_details, status):
        """Send notification about an application"""
        subject = f"Application {status}: {job_details['title']}"
        
        if status == "Applied":
            body = f"""
✅ Successfully applied to:

Job: {job_details['title']}
Company: {job_details['company']}
Location: {job_details['location']}

Your application has been submitted!
"""
        elif status == "Error":
            body = f"""
⚠️ Application Error:

Job: {job_details['title']}
Company: {job_details['company']}

There was an error applying to this position. Please check manually.
"""
        else:
            body = f"""
Job Application Update:

Job: {job_details['title']}
Company: {job_details['company']}
Status: {status}
"""
        
        return self.send_email(subject, body)
