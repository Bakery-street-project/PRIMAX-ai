# ==============================================================================
# PRIMSX CODEX - SCRIPT_2.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


# Generate Gmail + Sheets Progress Tracker Implementation
gmail_sheets_code = '''#!/usr/bin/env python3
"""
Codex SuperLab Gmail + Sheets Progress Tracker
Automated reminder system with progress analytics
"""

import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Environment configuration
GMAIL_CREDENTIALS = os.getenv("GMAIL_CREDENTIALS_PATH")
SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_PATH")
SHEETS_ID = os.getenv("PROGRESS_TRACKER_SHEET_ID")
NOTIFICATION_EMAIL = os.getenv("TEAM_NOTIFICATION_EMAIL")

class ProgressTracker:
    def __init__(self):
        self.gmail_service = self._init_gmail()
        self.sheets_client = self._init_sheets()
        self.worksheet = self.sheets_client.open_by_key(SHEETS_ID).sheet1
        
        # Load blueprint
        with open("codex_superlab_blueprint.json", "r") as f:
            self.blueprint = json.load(f)
    
    def _init_gmail(self):
        """Initialize Gmail API"""
        creds = Credentials.from_authorized_user_file(GMAIL_CREDENTIALS)
        return build('gmail', 'v1', credentials=creds)
    
    def _init_sheets(self):
        """Initialize Google Sheets API with gspread"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SHEETS_CREDENTIALS, scope
        )
        return gspread.authorize(creds)
    
    def initialize_tracker(self):
        """Initialize Google Sheet with blueprint data"""
        headers = [
            "Task ID", "Task Name", "Status", "Priority", 
            "Category", "Dependencies", "Last Updated", "Assignee", "Notes"
        ]
        
        # Clear existing data and set headers
        self.worksheet.clear()
        self.worksheet.append_row(headers)
        
        # Populate with blueprint tasks
        for phase_name, tasks in self.blueprint.items():
            for task in tasks:
                row = [
                    task["id"],
                    task["task"],
                    task["status"],
                    task["priority"],
                    task["category"],
                    ", ".join(task["dependencies"]),
                    datetime.now().isoformat(),
                    "",  # Assignee
                    phase_name
                ]
                self.worksheet.append_row(row)
        
        print("✅ Progress tracker initialized in Google Sheets")
    
    def get_all_tasks(self):
        """Fetch all tasks from sheet"""
        data = self.worksheet.get_all_records()
        return data
    
    def update_task_status(self, task_id, status, assignee="", notes=""):
        """Update task status in the sheet"""
        cell = self.worksheet.find(task_id)
        if cell:
            row = cell.row
            self.worksheet.update_cell(row, 3, status)  # Status column
            self.worksheet.update_cell(row, 7, datetime.now().isoformat())  # Last Updated
            if assignee:
                self.worksheet.update_cell(row, 8, assignee)  # Assignee
            if notes:
                current_notes = self.worksheet.cell(row, 9).value
                new_notes = f"{current_notes}\\n{datetime.now():%Y-%m-%d}: {notes}" if current_notes else notes
                self.worksheet.update_cell(row, 9, new_notes)
            
            print(f"✅ Updated {task_id} to {status}")
            return True
        return False
    
    def get_overdue_tasks(self):
        """Identify tasks that need attention"""
        tasks = self.get_all_tasks()
        overdue = []
        
        for task in tasks:
            # Critical tasks not started or stuck
            if task["Priority"] == "Critical" and task["Status"] in ["Not Started", ""]:
                overdue.append(task)
            
            # Tasks in progress for >7 days
            if task["Status"] == "In Progress" and task["Last Updated"]:
                try:
                    last_update = datetime.fromisoformat(task["Last Updated"])
                    if (datetime.now() - last_update).days > 7:
                        overdue.append(task)
                except:
                    pass
        
        return overdue
    
    def get_completion_stats(self):
        """Calculate completion statistics"""
        tasks = self.get_all_tasks()
        total = len(tasks)
        completed = sum(1 for t in tasks if t["Status"] == "Complete")
        in_progress = sum(1 for t in tasks if t["Status"] == "In Progress")
        not_started = sum(1 for t in tasks if t["Status"] in ["Not Started", ""])
        
        # By priority
        critical_complete = sum(1 for t in tasks if t["Priority"] == "Critical" and t["Status"] == "Complete")
        critical_total = sum(1 for t in tasks if t["Priority"] == "Critical")
        
        # By phase
        phase_stats = {}
        for task in tasks:
            phase = task.get("Notes", "Unknown")
            if phase not in phase_stats:
                phase_stats[phase] = {"total": 0, "completed": 0}
            phase_stats[phase]["total"] += 1
            if task["Status"] == "Complete":
                phase_stats[phase]["completed"] += 1
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "critical_completion": (critical_complete / critical_total * 100) if critical_total > 0 else 0,
            "phase_stats": phase_stats
        }
    
    def send_email(self, subject, body, to_email=None):
        """Send email via Gmail API"""
        if to_email is None:
            to_email = NOTIFICATION_EMAIL
        
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['subject'] = subject
        
        html_part = MIMEText(body, 'html')
        message.attach(html_part)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        try:
            self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            print(f"✅ Email sent: {subject}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
    
    def send_daily_digest(self):
        """Send daily progress digest"""
        stats = self.get_completion_stats()
        overdue = self.get_overdue_tasks()
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">🚀 Codex SuperLab Daily Progress Report</h2>
            
            <div style="background: #ecf0f1; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>📊 Overall Statistics</h3>
                <ul>
                    <li><strong>Total Tasks:</strong> {stats['total']}</li>
                    <li><strong>Completed:</strong> {stats['completed']} ({stats['completion_rate']:.1f}%)</li>
                    <li><strong>In Progress:</strong> {stats['in_progress']}</li>
                    <li><strong>Not Started:</strong> {stats['not_started']}</li>
                    <li><strong>Critical Task Completion:</strong> {stats['critical_completion']:.1f}%</li>
                </ul>
            </div>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>⚠️ Tasks Needing Attention ({len(overdue)})</h3>
                <ul>
        """
        
        for task in overdue[:10]:
            html_body += f"""
                    <li>
                        <strong>{task['Task ID']}</strong>: {task['Task Name']}<br>
                        <small>Priority: {task['Priority']} | Status: {task['Status']}</small>
                    </li>
            """
        
        html_body += """
                </ul>
            </div>
            
            <div style="background: #d1ecf1; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>📈 Phase Breakdown</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #17a2b8; color: white;">
                        <th style="padding: 10px; text-align: left;">Phase</th>
                        <th style="padding: 10px; text-align: center;">Progress</th>
                        <th style="padding: 10px; text-align: center;">%</th>
                    </tr>
        """
        
        for phase, data in stats['phase_stats'].items():
            pct = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
            bar_width = int(pct)
            html_body += f"""
                    <tr style="border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 10px;">{phase}</td>
                        <td style="padding: 10px; text-align: center;">{data['completed']}/{data['total']}</td>
                        <td style="padding: 10px; text-align: center;">
                            <div style="background: #e9ecef; width: 100px; height: 20px; border-radius: 10px; display: inline-block;">
                                <div style="background: #28a745; width: {bar_width}px; height: 20px; border-radius: 10px;"></div>
                            </div>
                            {pct:.0f}%
                        </td>
                    </tr>
            """
        
        html_body += """
                </table>
            </div>
            
            <p style="color: #6c757d; margin-top: 30px;">
                <em>This is an automated report from Codex SuperLab Progress Tracker</em><br>
                Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
            </p>
        </body>
        </html>
        """
        
        self.send_email(
            f"Codex SuperLab Progress Report - {datetime.now():%Y-%m-%d}",
            html_body
        )
    
    def send_task_reminder(self, task_id):
        """Send reminder for specific task"""
        tasks = self.get_all_tasks()
        task = next((t for t in tasks if t["Task ID"] == task_id), None)
        
        if not task:
            return False
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #e74c3c;">⏰ Task Reminder</h2>
            
            <div style="background: #fee; padding: 20px; border-left: 5px solid #e74c3c; margin: 20px 0;">
                <h3>{task['Task ID']}: {task['Task Name']}</h3>
                <p><strong>Priority:</strong> {task['Priority']}</p>
                <p><strong>Status:</strong> {task['Status']}</p>
                <p><strong>Category:</strong> {task['Category']}</p>
                
                {f"<p><strong>Dependencies:</strong> {task['Dependencies']}</p>" if task['Dependencies'] else ""}
                
                <p style="margin-top: 20px;">
                    This task needs your attention. Please update its status or provide progress notes.
                </p>
            </div>
            
            <p style="color: #6c757d;">
                <em>Automated reminder from Codex SuperLab</em>
            </p>
        </body>
        </html>
        """
        
        self.send_email(
            f"⏰ Reminder: {task['Task ID']} - {task['Task Name']}",
            html_body
        )
        return True

def main():
    """Main execution"""
    tracker = ProgressTracker()
    
    # Initialize if first run
    # tracker.initialize_tracker()  # Uncomment on first run
    
    # Send daily digest
    tracker.send_daily_digest()
    
    # Check and send reminders for overdue tasks
    overdue = tracker.get_overdue_tasks()
    for task in overdue:
        tracker.send_task_reminder(task["Task ID"])

if __name__ == "__main__":
    main()
'''

# Save Gmail + Sheets implementation
with open("gmail_sheets_progress_tracker.py", "w") as f:
    f.write(gmail_sheets_code)

print("Gmail + Sheets Progress Tracker created: gmail_sheets_progress_tracker.py")
