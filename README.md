# 🎯 Job Application Tracker Bot

An automated system for managing job applications with web scraping, application tracking, and reporting capabilities.

## ⚠️ Important Disclaimers

**Legal & Ethical Considerations:**

- Automating LinkedIn interactions may violate their Terms of Service
- Use this tool responsibly and at your own risk
- Consider using it primarily as a tracking tool rather than mass auto-applying
- Be respectful of companies' time - don't spam applications
- Your LinkedIn account may be suspended if detected

**We recommend using this bot in "tracking mode" rather than full automation.**

## ✨ Features

- 🔍 **Automated Job Discovery** - Scrape job listings from LinkedIn
- 🎯 **Smart Filtering** - Filter jobs based on your criteria
- 📝 **Auto-Application** - Apply to jobs with Easy Apply (optional)
- 💾 **Application Tracking** - SQLite database to track all applications
- 📬 **Follow-up Reminders** - Never miss a follow-up opportunity
- 📅 **Interview Scheduling** - Track and get reminders for interviews
- 📊 **Daily/Weekly Reports** - Beautiful HTML and Excel reports
- 📸 **Screenshot Capture** - Visual debugging for applications
- ⏰ **Automated Scheduler** - Run daily routines automatically

## 🚀 Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

**Required .env variables:**

```bash
# LinkedIn Credentials (required for scraping)
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Email Notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
NOTIFICATION_EMAIL=your_email@example.com
EMAIL_PASSWORD=your_app_password

# Application Settings
MAX_APPLICATIONS_PER_DAY=10
AUTO_APPLY_ENABLED=false  # Set to 'true' to enable auto-apply
```

### 3. Add Your Resume

```bash
# Place your resume in the outputs folder
cp /path/to/your/resume.pdf outputs/resumes/my_resume.pdf
```

### 4. Customize Job Criteria

Edit `config.py` to set your job search preferences:

```python
JOB_CRITERIA = {
    "keywords": ["Python Developer", "Backend Engineer"],
    "locations": ["Remote", "New York"],
    "blacklist_companies": ["BadCompany Inc"]
}
```

### 5. Run the Bot

```bash
# Interactive menu (recommended for first use)
python main.py

# Or use command-line mode
python main.py scrape      # Scrape jobs only
python main.py apply       # Run full daily routine
python main.py stats       # View statistics
python main.py scheduler   # Start automated scheduler
```

## 📖 Usage Guide

### Interactive Menu

Run `python main.py` to access the interactive menu:

```
🎯 JOB APPLICATION TRACKER BOT
===========================================

1. 🔍 Scrape jobs (no auto-apply)
2. 🚀 Run full daily routine
3. 📬 Check follow-ups
4. 📅 Check upcoming interviews
5. 📊 Generate daily report
6. 📈 Generate weekly report
7. 📋 List recent applications
8. 📊 View statistics
9. ⏰ Start scheduler (automated)
0. 🚪 Exit
```

### Command-Line Interface

```bash
# Scrape jobs without applying
python main.py scrape

# Run full daily routine (scrape + apply + report)
python main.py apply

# Check for follow-ups
python main.py followups

# Check upcoming interviews
python main.py interviews

# Generate reports
python main.py report     # Daily report
python main.py weekly     # Weekly report

# View statistics
python main.py stats 30   # Last 30 days

# List applications
python main.py list 50    # Show 50 recent applications

# Start automated scheduler
python main.py scheduler
```

### Automated Scheduler

The scheduler runs tasks at specific times:

- **8:00 AM** - Daily job search and applications
- **9:00 AM, 1:00 PM, 4:00 PM** - Interview reminders
- **Monday 9:00 AM** - Weekly review

```bash
python main.py scheduler
```

## 📁 Project Structure

```
job_application_tracker/
│
├── main.py                 # Main orchestrator
├── config.py              # Configuration
├── database.py            # SQLite operations
├── scraper.py             # Job scraping module
├── application_bot.py     # Auto-apply logic
├── tracker.py             # Status tracking
├── notifications.py       # Email/SMS alerts
├── reports.py             # Report generation
│
├── requirements.txt
├── .env                   # Your credentials (create from .env.template)
├── .env.template          # Environment template
├── .gitignore
│
├── database/
│   └── applications.db    # SQLite database (auto-created)
│
├── templates/
│   └── (HTML templates for reports)
│
└── outputs/
    ├── resumes/           # Your resume files
    │   └── my_resume.pdf
    ├── screenshots/       # Application screenshots
    └── reports/           # Generated reports
```

## 🛡️ Safety Features

- **Rate Limiting** - Delays between applications to avoid detection
- **Max Applications** - Daily limit to prevent spam
- **Screenshot Capture** - Visual debugging for errors
- **Manual Review Mode** - Flag applications needing manual input
- **Blacklist** - Avoid specific companies
- **Error Handling** - Graceful failures with screenshots

## ⚙️ Configuration Options

Edit `config.py` to customize:

### Job Search Criteria

```python
JOB_CRITERIA = {
    "keywords": ["Python Developer", "Backend Engineer"],
    "locations": ["Remote", "New York", "San Francisco"],
    "experience_level": ["Entry Level", "Mid Level"],
    "salary_range": {"min": 80000, "max": 200000},
    "job_types": ["Full-time", "Contract"],
    "blacklist_companies": ["BadCompany Inc"]
}
```

### Application Settings

```python
APPLICATION_SETTINGS = {
    "auto_apply": False,  # Enable auto-apply
    "max_applications_per_day": 10,
    "follow_up_days": 7,
    "avoid_quick_rejections": True
}
```

## 📊 Reports

The bot generates beautiful reports:

### Daily Reports

- Applications sent today
- Follow-ups needed
- Upcoming interviews
- Daily statistics

### Weekly Reports

- Total applications
- Interview rate
- Success metrics
- Detailed application list
- Excel export for analysis

Reports are saved in `outputs/reports/` as:

- HTML files (for viewing)
- Excel files (for data analysis)

## 🔧 Troubleshooting

### LinkedIn Login Issues

If login fails:

1. Check credentials in `.env`
2. LinkedIn may require 2FA - complete verification manually
3. Use `headless=False` in scraper to see browser

### No Jobs Found

- Verify your search criteria in `config.py`
- Check if LinkedIn requires login verification
- Try broader keywords or locations

### Email Notifications Not Working

- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
- Enable "Less secure app access" (not recommended) or use OAuth
- Verify SMTP settings in `.env`

### Database Errors

```bash
# Reset database (WARNING: Deletes all data)
rm database/applications.db
python -c "from database import ApplicationDatabase; ApplicationDatabase()"
```

## 🎓 Best Practices

1. **Start with Scraping Only** - Test with `AUTO_APPLY_ENABLED=false`
2. **Review Jobs First** - Use `python main.py list` to review scraped jobs
3. **Low Daily Limits** - Start with 5-10 applications per day
4. **Manual Applications** - Apply manually to high-priority jobs
5. **Regular Follow-ups** - Check follow-ups weekly
6. **Update Your Resume** - Keep `outputs/resumes/my_resume.pdf` current
7. **Monitor Screenshots** - Review `outputs/screenshots/` for errors

## 🚨 Known Limitations

- **LinkedIn Anti-Bot Measures** - May detect automation
- **Easy Apply Only** - External applications not supported
- **Form Limitations** - Complex forms may need manual input
- **Rate Limits** - Too many requests may trigger blocks
- **Browser Detection** - Headless mode may be detected

## 🔮 Future Enhancements

Potential features to add:

- [ ] Indeed.com scraping
- [ ] AI cover letter generation
- [ ] Resume tailoring per job
- [ ] Interview question preparation
- [ ] Salary negotiation tracker
- [ ] Company research integration
- [ ] Multi-user support
- [ ] API for external integrations

## 📝 License

This project is for educational purposes. Use responsibly and at your own risk. The authors are not responsible for any account bans or legal issues arising from use of this software.

## 🙏 Acknowledgments

Built with:

- [Playwright](https://playwright.dev/) - Browser automation
- [pandas](https://pandas.pydata.org/) - Data analysis
- [schedule](https://schedule.readthedocs.io/) - Task scheduling
- [Jinja2](https://jinja.palletsprojects.com/) - Template rendering

## 💡 Support

For issues or questions:

1. Check the troubleshooting section
2. Review screenshots in `outputs/screenshots/`
3. Check daily reports in `outputs/reports/`
4. Review the SQLite database directly

---

**Good luck with your job search! 🚀**
