# Codex SuperLab Automated Blueprint System
## Complete Setup & Implementation Guide

---

## 🎯 System Overview

The Codex SuperLab Automated Blueprint System is a comprehensive, AI-driven progress tracking and automation platform designed to:

- **Prevent Side-Tracking**: Automated checklists keep you focused on the roadmap
- **Track Progress**: Real-time updates across Discord, Gmail, and Google Sheets
- **Auto-Verify Completion**: CI/CD pipelines automatically check off completed tasks
- **Generate Content**: AI-powered super prompt system for cat articles and content creation
- **Rotate Secrets**: Automated token rotation for security compliance
- **Provide Analytics**: Predictive ML models for bottleneck detection

---

## 📦 System Components

### 1. Blueprint Data Structure
**File:** `codex_superlab_blueprint.json`

Contains 5 phases with 20 tasks:
- Phase 1: Foundation (Infrastructure setup)
- Phase 2: Automation (AI & bot development)
- Phase 3: Content Pipeline (Cat article system)
- Phase 4: Analytics (Predictive models)
- Phase 5: Production (SaaS deployment)

### 2. Discord Auto-Checker Bot
**File:** `discord_auto_checker_bot.py`

**Features:**
- Monitors task completion via commits and manual checks
- Real-time progress updates posted to Discord channels
- Commands: `!check`, `!progress`, `!blueprint`
- Auto-detects task mentions in commits
- Dependency validation before task completion

### 3. Gmail + Sheets Progress Tracker
**File:** `gmail_sheets_progress_tracker.py`

**Features:**
- Daily progress digest emails with charts
- Overdue task reminders
- Google Sheets integration for live dashboard
- Phase-by-phase completion statistics
- Beautiful HTML email templates

### 4. Cat Article Content Pipeline
**File:** `cat_article_content_pipeline.py`

**Features:**
- 8-stage content creation workflow
- AI-generated "super prompts" for each stage
- Context-aware prompt chaining
- Automatic stage advancement
- Integration with progress tracker

### 5. CI/CD Task Verification
**File:** `github_actions_task_verification.yml`

**Features:**
- Automated task verification via code analysis
- Monthly token rotation with validation
- Discord notifications for CI/CD events
- Artifact generation for audit trails
- Secure secret handling with git-crypt

---

## 🚀 Installation & Setup

### Prerequisites

```bash
# System Requirements
- Python 3.11+
- Git with git-crypt
- GPG for encryption
- Node.js 18+ (for some tools)

# API Accounts Needed
- Google Cloud Project (Sheets, Gmail APIs)
- Discord Bot Token
- OpenAI API Key (for super prompts)
- GitHub Personal Access Token
- Stripe API Keys (optional)
- Gumroad API Token (optional)
```

### Step 1: Clone and Initialize Vault

```bash
# Clone your Codex SuperLab repository
git clone https://github.com/YourUsername/codex-superlab.git
cd codex-superlab

# Initialize git-crypt for secret management
git-crypt init
gpg --gen-key  # Generate GPG key if you don't have one
git-crypt add-gpg-user YOUR_GPG_EMAIL

# Create API vault directory
mkdir -p ~/api-keys
cd ~/api-keys
git init
git-crypt init
```

### Step 2: Configure Environment Variables

Create `.env` file in `~/api-keys/`:

```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_PROGRESS_CHANNEL_ID=your_channel_id
DISCORD_PROGRESS_WEBHOOK=your_webhook_url
DISCORD_ADMIN_WEBHOOK=your_admin_webhook_url

# Google Cloud Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_SHEETS_SERVICE_ACCOUNT_PATH=/path/to/service_account.json
PROGRESS_TRACKER_SHEET_ID=your_sheet_id
CONTENT_TRACKER_SHEET_ID=your_content_sheet_id
GMAIL_CREDENTIALS_PATH=/path/to/gmail_credentials.json
TEAM_NOTIFICATION_EMAIL=your_email@example.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# GitHub Configuration
GITHUB_TOKEN=your_personal_access_token
VAULT_PATH=/home/yourusername/api-keys

# Stripe Configuration (Optional)
STRIPE_PUBLIC_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Gumroad Configuration (Optional)
GUMROAD_API_TOKEN=your_gumroad_token
```

### Step 3: Set Up Google Cloud APIs

```bash
# Enable required APIs
gcloud services enable sheets.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable drive.googleapis.com

# Create service account
gcloud iam service-accounts create codex-superlab \
    --display-name="Codex SuperLab Automation"

# Generate credentials
gcloud iam service-accounts keys create ~/api-keys/google_service_account.json \
    --iam-account=codex-superlab@your-project.iam.gserviceaccount.com

# For Gmail, set up OAuth2 credentials via Google Cloud Console
# Download as gmail_credentials.json
```

### Step 4: Initialize Google Sheets Tracker

```bash
# Create a new Google Sheet named "Codex SuperLab Progress"
# Share it with your service account email
# Copy the Sheet ID from the URL

# Initialize the tracker
python gmail_sheets_progress_tracker.py
# Uncomment tracker.initialize_tracker() on first run
```

### Step 5: Set Up Discord Bot

```bash
# Go to https://discord.com/developers/applications
# Create New Application → Bot → Add Bot
# Copy Bot Token to your .env file
# Enable Privileged Gateway Intents: Message Content

# Invite bot to your server with these permissions:
# - Send Messages
# - Embed Links
# - Read Message History
# - Use Slash Commands

# Create webhook for progress channel:
# Server Settings → Integrations → Webhooks → New Webhook
# Copy webhook URL to .env

# Run the bot
python discord_auto_checker_bot.py
```

### Step 6: Configure GitHub Actions

```bash
# Add secrets to your GitHub repository:
# Settings → Secrets and variables → Actions → New repository secret

# Required secrets:
- GPG_PRIVATE_KEY: Your GPG private key (export with: gpg --export-secret-keys --armor YOUR_KEY_ID)
- PAT_TOKEN: GitHub Personal Access Token
- DISCORD_PROGRESS_WEBHOOK: Discord webhook URL for CI/CD notifications
- DISCORD_ADMIN_WEBHOOK: Admin webhook for security alerts
- GOOGLE_SHEETS_CREDENTIALS: Content of google_service_account.json (base64 encoded)
- GMAIL_CREDENTIALS: Content of gmail_credentials.json (base64 encoded)
- DISCORD_BOT_TOKEN: Your bot token
- STRIPE_SECRET_KEY: Stripe secret key (if using)
- GMAIL_APP_PASSWORD: Gmail app password

# Copy workflow file to .github/workflows/
mkdir -p .github/workflows
cp github_actions_task_verification.yml .github/workflows/task_verification.yml

# Commit and push
git add .github/workflows/task_verification.yml
git commit -m "Add automated task verification workflow"
git push
```

### Step 7: Set Up Automated Reminders (Cron)

```bash
# Open crontab
crontab -e

# Add these entries:

# Daily progress digest at 9 AM
0 9 * * * cd /path/to/codex-superlab && /usr/bin/python3 gmail_sheets_progress_tracker.py

# Check for overdue tasks every 6 hours
0 */6 * * * cd /path/to/codex-superlab && /usr/bin/python3 gmail_sheets_progress_tracker.py

# Weekly comprehensive report on Mondays at 8 AM
0 8 * * 1 cd /path/to/codex-superlab && /usr/bin/python3 gmail_sheets_progress_tracker.py
```

---

## 💡 Usage Guide

### Creating a New Article Project

```python
from cat_article_content_pipeline import ContentPipeline

pipeline = ContentPipeline()

# Create new article
project = pipeline.create_article_project(
    topic="Understanding Cat Purring: Science and Meaning",
    target_date="2025-11-15"
)

# You'll receive a super prompt for the Idea Generation stage
# Complete that stage, then advance:

idea_output = {
    "selected_idea": "Comprehensive guide to purring science",
    "target_audience": "Cat owners and enthusiasts",
    "key_points": [...]
}

# Advance to next stage
pipeline.advance_stage(project["id"], idea_output)

# Repeat for each stage
```

### Checking Task Progress via Discord

```
# In your Discord server:

!progress all              # Show overall progress
!progress Phase_1_Foundation  # Show specific phase
!blueprint                 # Show full blueprint
!check F1                  # Manually check off task F1
```

### Manual Task Updates in Sheets

Open your Google Sheet and directly update:
- Status column: "Not Started" → "In Progress" → "Complete"
- Assignee column: Add team member name
- Notes column: Add progress notes

Changes sync automatically to Discord and email digests.

---

## 🤖 Automated Workflows

### Daily Automation Flow

1. **6 AM**: System checks for new commits
2. **9 AM**: Daily digest email sent to team
3. **12 PM**: Discord bot checks for stuck tasks
4. **6 PM**: Progress summary posted to Discord
5. **Continuous**: CI/CD pipeline verifies completed tasks on every commit

### Monthly Security Flow

1. **1st of month, 2 AM**: Token rotation workflow runs
2. Validates all API keys and tokens
3. Generates rotation report
4. Sends security digest to admin webhook
5. Creates audit trail artifacts

### Content Pipeline Flow

1. Create article project
2. AI generates super prompt for current stage
3. Complete stage (human or AI)
4. System auto-advances to next stage
5. New super prompt generated with context
6. Repeat until publication
7. Auto-posts to Discord when published

---

## 📊 Analytics & Dashboards

### Google Sheets Dashboard

Your tracker sheet includes:
- Real-time task status for all 20 blueprint tasks
- Phase completion percentages
- Overdue task highlighting (conditional formatting)
- Assignee workload distribution
- Historical progress over time

### Discord Progress Channel

Automated posts include:
- Task completion celebrations
- Milestone achievements
- Overdue task warnings
- Daily/weekly summaries
- CI/CD build status

### Email Digests

HTML-formatted emails with:
- Overall completion statistics
- Phase-by-phase breakdown with progress bars
- List of tasks needing attention
- Team member assignments
- Charts and visualizations

---

## 🔐 Security Best Practices

### Vault Management

```bash
# Rotate GitHub token
cd ~/api-keys
./rotate_github_token.sh

# Update token in .env
# Commit encrypted changes
git add .
git commit -m "chore: rotate GitHub token"
git push
```

### Secret Rotation Schedule

- **GitHub PAT**: Every 90 days (or on security event)
- **Discord Bot Token**: Every 180 days
- **Gmail App Password**: Every 90 days
- **API Keys (Stripe, Gumroad)**: Every 180 days or on breach
- **Google Service Account**: Annually

### Access Control

- Limit who has GPG keys to decrypt vault
- Use GitHub branch protection for automation files
- Enable 2FA on all service accounts
- Regular audit of access logs

---

## 🐛 Troubleshooting

### Discord Bot Not Responding

```bash
# Check if bot is running
ps aux | grep discord_auto_checker_bot.py

# Check logs
tail -f ~/codex-superlab/logs/discord_bot.log

# Restart bot
pkill -f discord_auto_checker_bot.py
python discord_auto_checker_bot.py &
```

### Gmail Not Sending

```bash
# Verify credentials
python -c "
from google.oauth2.credentials import Credentials
creds = Credentials.from_authorized_user_file('gmail_credentials.json')
print('Valid credentials' if creds.valid else 'Expired credentials')
"

# Refresh OAuth token if needed
# Re-run OAuth flow via Google Cloud Console
```

### Sheets Not Updating

```bash
# Check service account permissions
# Ensure sheet is shared with service account email

# Test connection
python -c "
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('google_service_account.json', scope)
client = gspread.authorize(creds)
print('Connection successful')
"
```

### CI/CD Pipeline Failing

```bash
# Check GitHub Actions logs
# Go to Actions tab in your repository
# Click on failed workflow run
# Review each step's logs

# Common issues:
- Secrets not configured correctly
- git-crypt decryption failing (check GPG key)
- Python dependencies not installing (check requirements.txt)
- API rate limits exceeded (check token validity)
```

---

## 🎨 Customization

### Adding New Blueprint Phases

Edit `codex_superlab_blueprint.json`:

```json
"Phase_6_YourPhase": [
  {
    "id": "YP1",
    "task": "Your task description",
    "category": "Your Category",
    "priority": "High",
    "dependencies": ["P4"],
    "automation": "What automation triggers this",
    "verification": "verification_script.py",
    "status": "Not Started"
  }
]
```

### Custom Article Templates

Modify `cat_article_content_pipeline.py`:

```python
# Add new content type
def create_video_script_project(self, topic, duration):
    # Similar to article pipeline but for video scripts
    pass
```

### Discord Command Extensions

Add to `discord_auto_checker_bot.py`:

```python
@bot.command(name="yourcommand")
async def your_command(ctx, arg: str):
    # Your custom command logic
    await ctx.send("Response")
```

---

## 📈 Performance Optimization

### Reduce API Calls

```python
# Cache Google Sheets data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_task_status(task_id):
    return task_manager.get_task_status(task_id)
```

### Optimize Discord Bot

```python
# Use Discord.py task loops instead of while True
from discord.ext import tasks

@tasks.loop(minutes=30)
async def periodic_check():
    # Your periodic task
    pass
```

---

## 🚀 Next Steps

1. **Week 1**: Set up infrastructure (Phase 1 tasks)
2. **Week 2-3**: Build automation layer (Phase 2 tasks)
3. **Week 4**: Implement content pipeline (Phase 3 tasks)
4. **Week 5**: Add analytics (Phase 4 tasks)
5. **Week 6+**: Production deployment (Phase 5 tasks)

---

## 📚 Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Google Sheets API Guide](https://developers.google.com/sheets/api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [git-crypt Guide](https://github.com/AGWA/git-crypt)

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs in `~/codex-superlab/logs/`
3. Post in Discord #support channel
4. Open GitHub issue with detailed description

---

**Last Updated**: October 21, 2025
**Version**: 1.0.0
**Maintainer**: Codex SuperLab Team
