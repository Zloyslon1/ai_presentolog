# Quick Start Guide

Get AI Presentolog up and running in 5-10 minutes!

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Google account
- [ ] 10 minutes of time
- [ ] Internet connection

---

## Step 1: Install (2 minutes)

### Clone or Download

```bash
# Option A: Clone with git
git clone <repository-url>
cd ai_presentolog

# Option B: Download and extract ZIP
# Then navigate to the folder
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Wait for installation to complete (may take 1-2 minutes)**

---

## Step 2: Google Cloud Setup (3 minutes)

### Quick OAuth Setup

1. **Go to:** [Google Cloud Console](https://console.cloud.google.com/)

2. **Create Project:**
   - Click "Select a project" → "New Project"
   - Name: "AI Presentolog"
   - Click "Create"

3. **Enable APIs:**
   - Search "Google Slides API" → Enable
   - Search "Google Drive API" → Enable

4. **OAuth Consent Screen:**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Select "External" → Create
   - Fill in:
     - App name: AI Presentolog
     - Your email (2 fields)
   - Save and Continue (3 times)

5. **Create Credentials:**
   - "APIs & Services" → "Credentials"
   - "Create Credentials" → "OAuth client ID"
   - Type: "Desktop app"
   - Name: "AI Presentolog"
   - Create → Download JSON

6. **Place Credentials:**
   ```bash
   # Create credentials folder
   mkdir credentials
   
   # Move downloaded file (adjust path as needed)
   # Windows
   move "%USERPROFILE%\Downloads\client_secret*.json" credentials\client_secret.json
   
   # macOS/Linux
   mv ~/Downloads/client_secret*.json credentials/client_secret.json
   ```

**Done!** OAuth is configured.

---

## Step 3: Start Application (30 seconds)

```bash
python web_app.py
```

**You should see:**
```
Database initialized at db/presentation_jobs.db
 * Running on http://localhost:5000
```

---

## Step 4: First Login (1 minute)

1. **Open browser:** http://localhost:5000

2. **Click:** "Sign in with Google"

3. **Select** your Google account

4. **Review permissions** and click "Allow"

5. **You're in!** You should see the main interface with your email in the navigation bar.

---

## Step 5: Process Your First Presentation (2 minutes)

### Option A: From Google Slides URL

1. **Find a presentation:**
   - Go to [Google Slides](https://slides.google.com)
   - Open or create a presentation
   - Copy the URL

2. **In AI Presentolog:**
   - Paste the URL
   - Click "📝 Открыть редактор" (Open Editor)
   - Wait for extraction (10-30 seconds)

3. **Edit and Generate:**
   - Make edits in the interactive editor
   - Select template and settings
   - Click "Создать презентацию" (Create Presentation)
   - Access your styled presentation in Google Slides!

### Option B: From Text

1. **Prepare text content:**
   ```
   My Presentation Title
   
   # First Slide
   This is the main content of slide 1
   - Bullet point 1
   - Bullet point 2
   
   # Second Slide
   Content for slide 2
   ```

2. **In AI Presentolog:**
   - Select "Текст" (Text) tab
   - Paste your content
   - Click "📝 Открыть редактор"

3. **Edit and Generate:**
   - Review extracted slides
   - Make edits as needed
   - Generate presentation

---

## What's Next?

### Learn More Features

- **[Web Interface Guide](../user-guide/web-interface.md)** - Full interface tour
- **[Slide Editor](../user-guide/slide-editor.md)** - Editor features
- **[Templates](../user-guide/templates.md)** - Using design templates

### Customize

- **[Template Development](../developer-guide/template-development.md)** - Create custom templates
- **[API Reference](../developer-guide/api-reference.md)** - Use Python API

### Deploy

- **[Production Deployment](../deployment/production.md)** - Deploy to server

---

## Troubleshooting Quick Fixes

### Can't install dependencies

```bash
# Try with python3
python3 -m pip install -r requirements.txt
```

### "Client secrets not found"

**Check file location:**
```bash
# Should show the file
ls credentials/client_secret.json  # macOS/Linux
dir credentials\client_secret.json  # Windows
```

**If missing:** Re-download from Google Cloud Console and place in `credentials/`

### OAuth error "redirect_uri_mismatch"

**This is normal for Desktop app!** Click through the warning:
- Click "Advanced"
- Click "Go to AI Presentolog (unsafe)"
- This is safe for your own development

### Application won't start

**Check Python version:**
```bash
python --version
# Should be 3.8 or higher
```

**Check port availability:**
```bash
# Try different port
python web_app.py --port 8080
```

### Can't access presentation

**Make sure:**
- Presentation exists and you have access
- OR presentation is shared with "Anyone with link"
- You're signed in with correct Google account

---

## Environment Variables (Optional)

For better security, set these before starting:

```bash
# Windows (PowerShell)
$env:SECRET_KEY = "your-random-secret-key-here"
$env:OAUTHLIB_INSECURE_TRANSPORT = "1"  # Local development only

# macOS/Linux
export SECRET_KEY="your-random-secret-key-here"
export OAUTHLIB_INSECURE_TRANSPORT=1  # Local development only
```

---

## Quick Reference Commands

```bash
# Start application
python web_app.py

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/unit/test_local.py

# Check database
python tests/debug/check_db.py

# List templates
python -m presentation_design.main --list-templates
```

---

## Getting Help

- **[Installation Guide](installation.md)** - Detailed setup instructions
- **[Authentication Guide](authentication.md)** - OAuth details
- **[Troubleshooting](../user-guide/troubleshooting.md)** - Common issues
- **[Full Documentation](../../README.md)** - Complete docs

---

## Success Checklist

After completing this guide, you should have:

- [x] AI Presentolog installed
- [x] Google OAuth configured
- [x] Application running on localhost:5000
- [x] Signed in with Google account
- [x] Processed at least one presentation
- [x] Seen the interactive editor
- [x] Generated a styled presentation

**Congratulations!** You're ready to use AI Presentolog. 🎉

---

**Last Updated:** December 17, 2024
