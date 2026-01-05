# Quick Start Guide - Updated Bot

## Installation Steps

### 1. Install Dependencies

```bash
cd "/Users/app/Desktop/Job Application Tracker Bot"

# If you have a virtual environment, activate it first
# source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install new packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.template .env

# Edit with your credentials
nano .env  # or use VSCode, TextEdit, etc.
```

**Required settings in .env:**

- `LINKEDIN_EMAIL` - Your LinkedIn email
- `LINKEDIN_PASSWORD` - Your LinkedIn password

**Optional but recommended:**

- `NOTIFICATION_EMAIL` - Email for notifications
- `EMAIL_PASSWORD` - App password for Gmail
- `AUTO_APPLY_ENABLED=false` - Keep false initially!

### 3. Test the Bot

```bash
# Test that everything works
python main.py

# Try scraping jobs (no auto-apply)
# Select option 1 from the menu
```

## What's Different?

### Session Persistence

- **First run**: Bot logs in and saves session to `.sessions/`
- **Next runs**: Bot reuses session (no login for 7 days!)
- You'll see: "✓ Session is valid, skipping login!"

### Colored Logging

- Green = INFO (normal operations)
- Yellow = WARNING (potential issues)
- Red = ERROR (failures)
- All logs also saved to `logs/bot_YYYYMMDD.log`

### Better Error Handling

- Network failures retry automatically (3 times)
- Clear error messages tell you what went wrong
- LinkedIn verification prompts guide you through security checks

## Quick Test

Run this to verify everything is set up:

```bash
python -c "from config import *; from logger import *; print('✅ All modules loaded successfully!')"
```

If you see the success message, you're ready to go!

## Troubleshooting

### Virtual Environment Issues

If you see "ModuleNotFoundError", make sure you're in your virtual environment:

```bash
# Create venv if you don't have one
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Missing .env File

```bash
# Make sure you copied the template
ls -la .env  # Should show the file

# If not found:
cp .env.template .env
```

## Next Steps

1. ✅ Run `python main.py`
2. ✅ Choose option 1 (Scrape jobs)
3. ✅ Review scraped jobs
4. ✅ Check logs in `logs/` directory
5. ✅ Verify session saved in `.sessions/`

Enjoy your improved bot! 🎉
