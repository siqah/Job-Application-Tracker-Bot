from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from jinja2 import Template
from database import ApplicationDatabase
from config import REPORTS_DIR, TEMPLATES_DIR

class ReportGenerator:
    def __init__(self):
        self.db = ApplicationDatabase()
        self.reports_dir = REPORTS_DIR
        self.templates_dir = TEMPLATES_DIR
    
    def generate_daily_report(self):
        """Generate a daily application report"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's applications
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT * FROM applications 
        WHERE date_applied = ? 
        ORDER BY id DESC
        ''', (today,))
        todays_apps = cursor.fetchall()
        
        # Get today's stats
        stats = self.db.get_daily_stats(today)
        
        # Get pending follow-ups
        followups = self.db.get_pending_followups()
        
        # Get upcoming interviews
        interviews = self.db.get_upcoming_interviews(7)
        
        # Generate HTML report
        report_html = self._generate_html_report(
            title=f"Daily Report - {today}",
            applications=todays_apps,
            stats=stats,
            followups=followups,
            interviews=interviews
        )
        
        # Save report
        report_path = self.reports_dir / f"daily_report_{today}.html"
        with open(report_path, 'w') as f:
            f.write(report_html)
        
        print(f"✓ Daily report generated: {report_path.name}")
        return str(report_path)
    
    def generate_weekly_report(self):
        """Generate a weekly summary report"""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        # Get week's applications
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT * FROM applications 
        WHERE date_applied >= ? 
        ORDER BY date_applied DESC
        ''', (week_ago.strftime('%Y-%m-%d'),))
        weeks_apps = cursor.fetchall()
        
        # Get statistics
        stats = self.db.get_stats_summary(7)
        
        # Generate report
        report_data = {
            'start_date': week_ago.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d'),
            'total_applications': len(weeks_apps),
            'stats': stats,
            'applications': weeks_apps
        }
        
        # Create Excel report
        excel_path = self.reports_dir / f"weekly_report_{today.strftime('%Y-%m-%d')}.xlsx"
        self._generate_excel_report(weeks_apps, excel_path)
        
        # Create HTML report
        html_report = self._generate_html_report(
            title=f"Weekly Report - {week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}",
            applications=weeks_apps,
            stats=stats,
            followups=[],
            interviews=[]
        )
        
        html_path = self.reports_dir / f"weekly_report_{today.strftime('%Y-%m-%d')}.html"
        with open(html_path, 'w') as f:
            f.write(html_report)
        
        print(f"✓ Weekly reports generated:")
        print(f"   HTML: {html_path.name}")
        print(f"   Excel: {excel_path.name}")
        
        return str(html_path)
    
    def _generate_html_report(self, title, applications, stats, followups, interviews):
        """Generate HTML report from template"""
        template_html = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .section { 
            background: white; 
            padding: 20px; 
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; margin-top: 5px; }
        table { 
            width: 100%; 
            border-collapse: collapse;
        }
        th { 
            background: #667eea; 
            color: white; 
            padding: 12px;
            text-align: left;
        }
        td { 
            padding: 12px; 
            border-bottom: 1px solid #eee;
        }
        tr:hover { background: #f9f9f9; }
        .status-applied { color: #2196F3; font-weight: bold; }
        .status-interview { color: #4CAF50; font-weight: bold; }
        .status-rejected { color: #f44336; font-weight: bold; }
        .status-offer { color: #FF9800; font-weight: bold; }
        h2 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .empty-state { 
            text-align: center; 
            color: #999; 
            padding: 40px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p>Generated on {{ now }}</p>
    </div>
    
    {% if stats %}
    <div class="section">
        <h2>📊 Statistics</h2>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_applications or 0 }}</div>
                <div class="stat-label">Total Applications</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.interviews or 0 }}</div>
                <div class="stat-label">Interviews</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.rejections or 0 }}</div>
                <div class="stat-label">Rejections</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.offers or 0 }}</div>
                <div class="stat-label">Offers</div>
            </div>
        </div>
    </div>
    {% endif %}
    
    <div class="section">
        <h2>📝 Applications</h2>
        {% if applications %}
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for app in applications %}
                <tr>
                    <td>{{ app.date_applied }}</td>
                    <td><strong>{{ app.job_title }}</strong></td>
                    <td>{{ app.company_name }}</td>
                    <td>{{ app.location }}</td>
                    <td class="status-{{ app.application_status.lower().replace(' ', '-') }}">
                        {{ app.application_status }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">No applications in this period</div>
        {% endif %}
    </div>
    
    {% if followups %}
    <div class="section">
        <h2>📬 Follow-ups Needed</h2>
        <table>
            <thead>
                <tr>
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Applied</th>
                    <th>Follow-up Date</th>
                </tr>
            </thead>
            <tbody>
                {% for app in followups %}
                <tr>
                    <td><strong>{{ app.job_title }}</strong></td>
                    <td>{{ app.company_name }}</td>
                    <td>{{ app.date_applied }}</td>
                    <td>{{ app.follow_up_date }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}
    
    {% if interviews %}
    <div class="section">
        <h2>📅 Upcoming Interviews</h2>
        <table>
            <thead>
                <tr>
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Interview Date</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                {% for app in interviews %}
                <tr>
                    <td><strong>{{ app.job_title }}</strong></td>
                    <td>{{ app.company_name }}</td>
                    <td>{{ app.interview_date }}</td>
                    <td>{{ app.notes or '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}
</body>
</html>
"""
        
        template = Template(template_html)
        return template.render(
            title=title,
            now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            applications=applications,
            stats=stats,
            followups=followups,
            interviews=interviews
        )
    
    def _generate_excel_report(self, applications, output_path):
        """Generate Excel report"""
        if not applications:
            # Create empty DataFrame
            df = pd.DataFrame(columns=['Date Applied', 'Job Title', 'Company', 'Location', 'Status'])
        else:
            # Convert to DataFrame
            data = []
            for app in applications:
                data.append({
                    'Date Applied': app['date_applied'],
                    'Job Title': app['job_title'],
                    'Company': app['company_name'],
                    'Location': app['location'],
                    'Status': app['application_status'],
                    'Salary Range': app['salary_range'],
                    'Follow-up Date': app['follow_up_date'],
                    'Interview Date': app['interview_date'] or '',
                    'Notes': app['notes'] or '',
                    'Job URL': app['job_url']
                })
            
            df = pd.DataFrame(data)
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Applications', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Applications']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def close(self):
        """Close database connection"""
        self.db.close()
