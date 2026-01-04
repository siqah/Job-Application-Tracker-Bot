import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database" / "applications.db"
RESUME_PATH = BASE_DIR / "outputs" / "resumes" / "my_resume.pdf"
SCREENSHOTS_DIR = BASE_DIR / "outputs" / "screenshots"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"

# Job Search Criteria
JOB_CRITERIA = {
    "keywords": ["Python Developer", "Reactjs Developer", "Software Engineer", "Fullstack Developer", "Fullstack Engineer", "Frontend Developer"],
    "locations": ["Remote", "New York", "San Francisco"],
    "experience_level": ["Entry Level", "Mid Level", "Senior Level"],
    "salary_range": {"min": 40000, "max": 200000},
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

# Create necessary directories
for directory in [SCREENSHOTS_DIR, REPORTS_DIR, DB_PATH.parent, TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
