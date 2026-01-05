import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_environment():
    """Validate required environment variables are set"""
    required_vars = ['LINKEDIN_EMAIL', 'LINKEDIN_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n" + "="*60)
        print("❌ CONFIGURATION ERROR")
        print("="*60)
        print("\nThe following required environment variables are missing:\n")
        for var in missing_vars:
            print(f"  • {var}")
        print("\nPlease:")
        print("  1. Copy .env.template to .env")
        print("  2. Fill in your credentials")
        print("  3. Run the bot again\n")
        print("="*60 + "\n")
        sys.exit(1)
    
    # Warn about optional settings
    optional_vars = ['NOTIFICATION_EMAIL', 'EMAIL_PASSWORD']
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_optional:
        print("\n⚠️  Optional email notifications disabled (missing credentials)")
        print("   Configure NOTIFICATION_EMAIL and EMAIL_PASSWORD in .env to enable\n")


# Validate on import
validate_environment()

# Paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database" / "applications.db"
RESUME_PATH = BASE_DIR / "outputs" / "resumes" / "my_resume.pdf"
SCREENSHOTS_DIR = BASE_DIR / "outputs" / "screenshots"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
SESSIONS_DIR = BASE_DIR / ".sessions"  # Browser session storage
LOGS_DIR = BASE_DIR / "logs"  # Log files directory

# Job Search Criteria
JOB_CRITERIA = {
    "keywords": ["Python Developer", "Reactjs Developer", "Software Engineer", "Fullstack Developer", "Fullstack Engineer", "Frontend Developer"],
    "locations": ["Remote", "Nairobi", "Kenya", "Mombasa", "Nakuru"],
    "experience_level": ["Entry Level", "Mid Level", "Senior Level"],
    "salary_range": {"min": 30000, "max": 200000},
    "job_types": ["Full-time", "Contract", "Part-time", "Internship", "Freelance", "Temporary", "Seasonal", "Hourly", "Commission", "Piecework", "Consultant", "Co-op", "Apprenticeship", "Trainee", "Volunteer", "Other"],
    "blacklist_companies": ["BadCompany Inc", "Exploitative Corp"]
}

# Application Settings
APPLICATION_SETTINGS = {
    "auto_apply": os.getenv("AUTO_APPLY_ENABLED", "false").lower() == "true",
    "max_applications_per_day": int(os.getenv("MAX_APPLICATIONS_PER_DAY", "10")),
    "cover_letter_template": TEMPLATES_DIR / "cover_letter.txt",
    "follow_up_days": 7,
    "avoid_quick_rejections": True
}

# Credentials (store in .env file)
LINKEDIN_CREDENTIALS = {
    "email": os.getenv("LINKEDIN_EMAIL"),
    "password": os.getenv("LINKEDIN_PASSWORD")
}

EMAIL_SETTINGS = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "email": os.getenv("NOTIFICATION_EMAIL"),
    "password": os.getenv("EMAIL_PASSWORD")
}

# User Information (for applications)
USER_INFO = {
    "phone": os.getenv("USER_PHONE", "123-456-7890"),
    "city": os.getenv("USER_CITY", "New York"),
    "website": os.getenv("USER_WEBSITE", "")
}

# Retry and Rate Limiting Settings
RETRY_SETTINGS = {
    "max_attempts": int(os.getenv("MAX_RETRIES", "3")),
    "wait_min": 1,  # Minimum wait between retries (seconds)
    "wait_max": 10,  # Maximum wait between retries (seconds)
    "exponential_base": 2  # Exponential backoff multiplier
}

# Browser Settings
BROWSER_SETTINGS = {
    "headless": os.getenv("HEADLESS_MODE", "true").lower() == "true",
    "slow_mo": 500,  # Slow down actions by milliseconds
    "timeout": 30000  # Default timeout in milliseconds
}

# Create necessary directories
for directory in [SCREENSHOTS_DIR, REPORTS_DIR, DB_PATH.parent, TEMPLATES_DIR, SESSIONS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
